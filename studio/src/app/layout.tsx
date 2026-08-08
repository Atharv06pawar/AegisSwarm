import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Newsreader } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme/ThemeProvider";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { AppShell } from "@/components/layout/AppShell";

const fontSans = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const fontMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

const fontHeading = Newsreader({
  subsets: ["latin"],
  variable: "--font-heading",
  style: ["normal", "italic"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "AegisSwarm Studio | Universal AI Attack Ontology & Red Teaming Platform",
  description: "Universal language and streaming data lake platform for AI security attacks and red teaming.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`dark ${fontSans.variable} ${fontMono.variable} ${fontHeading.variable}`}
      style={{ colorScheme: "dark" }}
    >
      <body className="font-sans antialiased bg-[#080c14] text-slate-100">
        <QueryProvider>
          <ThemeProvider
            attribute="class"
            defaultTheme="dark"
            enableSystem={false}
            disableTransitionOnChange
          >
            <AppShell>{children}</AppShell>
          </ThemeProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
