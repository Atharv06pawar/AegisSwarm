import sys
import json
import logging
import tempfile
from typing import List, Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler

from core.registry import PluginRegistry
from core.orchestrator import PipelineOrchestrator
from configs.settings import AegisSettings
from storage.data_lake import JSONLBackend, ParquetBackend

app = typer.Typer(
    name="aegisswarm",
    help="AegisSwarm V2 CLI - Production-grade autonomous AI attack dataset ingestion pipeline.",
    add_completion=False,
)
console = Console()

__version__ = "2.0.0"

def setup_logging(verbose: bool):
    """Configures structured, visually rich logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console, show_path=verbose)]
    )
    # Silence overly verbose third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def _build_orchestrator(config_file: str, dry_run: bool) -> PipelineOrchestrator:
    """Helper to construct the orchestrator based on settings."""
    settings = AegisSettings.from_yaml(config_file)
    
    registry = PluginRegistry()
    registry.discover(settings.plugins.package_path)
    
    # Configure Storage Backend
    if dry_run:
        base_path = tempfile.mkdtemp(prefix="aegisswarm_dryrun_")
        console.print(f"[bold yellow]DRY-RUN MODE:[/bold yellow] Output redirecting to transient directory: {base_path}")
    else:
        base_path = settings.paths.lake_dir
        
    if settings.storage.backend.lower() == "parquet":
        storage = ParquetBackend(base_path=base_path, compression=settings.storage.compression)
    else:
        storage = JSONLBackend(base_path=base_path, compression=settings.storage.compression)
        
    return PipelineOrchestrator(
        storage_backend=storage,
        plugin_registry=registry,
        batch_size=settings.storage.batch_size,
        checkpoint_dir=settings.paths.checkpoint_dir
    )

@app.command()
def version():
    """Display the AegisSwarm version."""
    console.print(f"[bold blue]AegisSwarm Engine[/bold blue] v{__version__}")

@app.command()
def discover(
    config: str = typer.Option("configs/settings.yaml", "--config", "-c", help="Path to YAML configuration file.")
):
    """Actively sweep the plugins directory and validate architectures."""
    settings = AegisSettings.from_yaml(config)
    registry = PluginRegistry()
    
    console.print(f"Scanning package '{settings.plugins.package_path}' for compatible plugins...")
    try:
        registry.discover(settings.plugins.package_path)
        plugins = registry.list_plugins()
        console.print(f"[bold green]Success![/bold green] Found {len(plugins)} compliant dataset plugins.")
    except Exception as e:
        console.print(f"[bold red]Discovery failed:[/bold red] {e}")
        sys.exit(1)

@app.command()
def list_plugins(
    config: str = typer.Option("configs/settings.yaml", "--config", "-c", help="Path to YAML configuration file.")
):
    """List all registered dataset plugins ready for ingestion."""
    settings = AegisSettings.from_yaml(config)
    registry = PluginRegistry()
    registry.discover(settings.plugins.package_path)
    
    plugins = registry.list_plugins()
    console.print(f"[bold cyan]Available Datasets ({len(plugins)}):[/bold cyan]")
    for p in plugins:
        plugin_class = registry.get_plugin(p)
        instance = plugin_class()
        console.print(f"  - [bold]{p}[/bold] (v{instance.parser_version})")

@app.command()
def ingest(
    datasets: Optional[List[str]] = typer.Argument(None, help="Specific dataset_ids to ingest. Leave empty for all."),
    config: str = typer.Option("configs/settings.yaml", "--config", "-c", help="Path to YAML configuration file."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging output."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Run ingestion safely into a temporary directory without affecting the Data Lake.")
):
    """
    Run the core ingestion pipeline. Streams, normalizes, and partitions data dynamically.
    """
    setup_logging(verbose)
    
    # We use Rich Progress bars alongside the logger for highly visual tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=False,
        console=console
    ) as progress:
        task_id = progress.add_task(description="Initializing AegisSwarm Orchestrator...", total=None)
        
        try:
            orchestrator = _build_orchestrator(config, dry_run)
            available_plugins = orchestrator.plugin_registry.list_plugins()
            
            to_run = datasets if datasets else available_plugins
            if not to_run:
                progress.update(task_id, description="[bold yellow]No datasets found to run.[/bold yellow]")
                return

            for dataset_id in to_run:
                if dataset_id not in available_plugins:
                    console.print(f"[bold red]Error:[/bold red] Plugin '{dataset_id}' not found in registry.")
                    continue
                    
                progress.update(task_id, description=f"Ingesting dataset stream: [bold]{dataset_id}[/bold]")
                orchestrator.run_plugin(dataset_id)
                
            progress.update(task_id, description="Committing reproducibility manifest...")
            manifest_path = orchestrator.lineage_tracker.save_manifest()
            
            progress.update(task_id, description="[bold green]Ingestion Pipeline Successfully Completed![/bold green]")
            
            console.print("\n[bold cyan]Run Statistics:[/bold cyan]")
            console.print(json.dumps(orchestrator.stats, indent=4))
            console.print(f"[dim]Lineage stored at: {manifest_path}[/dim]")
            
        except KeyboardInterrupt:
            console.print("\n[bold red]Pipeline interrupted by user.[/bold red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"\n[bold red]Pipeline encountered a fatal error:[/bold red] {e}")
            sys.exit(1)

@app.command()
def validate(
    dataset_id: str = typer.Argument(..., help="The exact dataset_id to validate."),
    config: str = typer.Option("configs/settings.yaml", "--config", "-c", help="Path to YAML configuration file.")
):
    """
    Run strict validation constraints over a plugin's raw data.
    Implicitly uses dry-run mode to ensure no dirty data touches the Data Lake.
    """
    setup_logging(verbose=True)
    console.print(f"[bold yellow]Validation Mode Initiated for '{dataset_id}'...[/bold yellow]")
    
    orchestrator = _build_orchestrator(config, dry_run=True)
    
    if dataset_id not in orchestrator.plugin_registry.list_plugins():
        console.print(f"[bold red]Error: Plugin '{dataset_id}' not found.[/bold red]")
        sys.exit(1)
        
    orchestrator.run_plugin(dataset_id)
    
    stats = orchestrator.stats.get(dataset_id, {})
    errors = stats.get("errors", 0)
    
    if errors > 0:
        console.print(f"[bold red]Validation failed with {errors} batch errors.[/bold red]")
        sys.exit(1)
    else:
        console.print("[bold green]Validation Complete. Data strictly conforms to AegisSwarm Schema.[/bold green]")

@app.command()
def stats(
    config: str = typer.Option("configs/settings.yaml", "--config", "-c", help="Path to YAML configuration file.")
):
    """
    Display high-level analytical statistics about the current Data Lake contents.
    """
    settings = AegisSettings.from_yaml(config)
    manifest_dir = Path(settings.paths.manifest_dir)
    
    if not manifest_dir.exists():
        console.print("[bold yellow]No manifests found. The Data Lake is currently empty.[/bold yellow]")
        return
        
    manifests = list(manifest_dir.glob("*.json"))
    console.print(f"[bold cyan]Data Lake Analytics[/bold cyan]")
    console.print(f"Total Historical Ingestion Runs: {len(manifests)}")
    
    # Just grab the latest one for display
    latest_manifest = sorted(manifests, key=lambda p: p.stat().st_mtime)[-1]
    with open(latest_manifest, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    console.print(f"\n[bold]Latest Run ({data.get('manifest_id')}):[/bold]")
    for record in data.get("records", []):
        ds_id = record.get("dataset_id")
        parts = len(record.get("output_partitions", []))
        console.print(f"  - {ds_id}: Generated {parts} partition chunks.")

if __name__ == "__main__":
    app()
