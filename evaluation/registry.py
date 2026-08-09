"""
EvaluatorRegistry for dynamic discovery and registration of BaseEvaluator implementations.
"""

import importlib
import pkgutil
import logging
from typing import Dict, Type, List, Optional
from evaluation.base import BaseEvaluator
from evaluation.exceptions import EvaluatorNotFound

logger = logging.getLogger(__name__)


class EvaluatorRegistry:
    """
    Registry class maintaining registered BaseEvaluator implementation classes.
    Supports manual registration, dynamic discovery from evaluation/evaluators, and class lookup.
    """

    _registry: Dict[str, Type[BaseEvaluator]] = {}

    @classmethod
    def register(cls, evaluator_cls: Type[BaseEvaluator], name: Optional[str] = None) -> None:
        """
        Registers a BaseEvaluator implementation class.
        
        Args:
            evaluator_cls (Type[BaseEvaluator]): The evaluator class inheriting from BaseEvaluator.
            name (Optional[str]): Optional custom name override.
        """
        if not issubclass(evaluator_cls, BaseEvaluator):
            raise TypeError(f"Class '{evaluator_cls.__name__}' must inherit from BaseEvaluator.")

        try:
            temp_name = evaluator_cls.name.fget(None) if isinstance(evaluator_cls.name, property) else name
        except Exception:
            temp_name = name or evaluator_cls.__name__.lower()

        final_key = (name or temp_name or evaluator_cls.__name__).lower()
        cls._registry[final_key] = evaluator_cls
        logger.info(f"Registered evaluator: '{final_key}' ({evaluator_cls.__name__})")

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Unregisters an evaluator class by name.
        """
        key = name.lower()
        if key in cls._registry:
            del cls._registry[key]
            logger.info(f"Unregistered evaluator: '{key}'")

    @classmethod
    def clear(cls) -> None:
        """
        Clears all registered evaluators.
        """
        cls._registry.clear()

    @classmethod
    def discover(cls) -> List[str]:
        """
        Dynamically discovers and registers all evaluators in evaluation/evaluators/.
        
        Returns:
            List[str]: Names of registered evaluators.
        """
        try:
            import evaluation.evaluators as evaluators_pkg
            for _, module_name, _ in pkgutil.iter_modules(evaluators_pkg.__path__):
                full_module_name = f"evaluation.evaluators.{module_name}"
                mod = importlib.import_module(full_module_name)
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseEvaluator) and attr is not BaseEvaluator:
                        ev_name = getattr(attr, "name", None)
                        if isinstance(ev_name, property):
                            try:
                                inst = attr()
                                ev_name = inst.name
                            except Exception:
                                ev_name = module_name
                        elif not ev_name:
                            ev_name = module_name
                        cls.register(attr, name=str(ev_name))
        except Exception as e:
            logger.warning(f"Error during evaluator discovery: {e}")

        return cls.list_evaluators()

    @classmethod
    def list_evaluators(cls) -> List[str]:
        """
        Returns a sorted list of registered evaluator names.
        """
        return sorted(list(cls._registry.keys()))

    @classmethod
    def get_evaluator(cls, name: str) -> Type[BaseEvaluator]:
        """
        Retrieves the evaluator class by name.
        
        Raises:
            EvaluatorNotFound: If evaluator name is not registered.
        """
        key = name.lower()
        if key not in cls._registry:
            if not cls._registry:
                cls.discover()
            if key not in cls._registry:
                raise EvaluatorNotFound(name)
        return cls._registry[key]
