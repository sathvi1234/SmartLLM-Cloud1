import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SmartLLM Cloud — LLM Optimization Middleware",
  description:
    "Analyze, optimize, and route LLM requests across OpenAI, Gemini, Groq and Ollama with real token, cost and latency tracking.",
  keywords: ["LLM", "optimization", "routing", "cost", "tokens", "SmartLLM"],
  authors: [{ name: "SmartLLM Cloud" }],
  openGraph: {
    title: "SmartLLM Cloud — LLM Optimization Middleware",
    description: "Measurable LLM optimization: routing, cost, tokens and latency",
    type: "website",
  },
};

export const viewport: Viewport = {
  themeColor: "#09090F",
  colorScheme: "dark",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} dark`} suppressHydrationWarning>
      <body className="font-sans antialiased bg-[#09090F] text-white">
        {children}
      </body>
    </html>
  );
}
