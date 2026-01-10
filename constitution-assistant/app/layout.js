import './globals.css'

export const metadata = {
  title: 'Constitution Assistant',
  description: 'AI-powered chatbot for constitution inquiries',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
