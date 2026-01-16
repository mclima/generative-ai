import "./globals.css";

export const metadata = {
  title: "Agentic Tech Job Board",
  description: "AI-powered job board for tech positions",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <title>Agentic Tech Job Board</title>
      </head>
      <body>
        <main>{children}</main>
      </body>
    </html>
  );
}
