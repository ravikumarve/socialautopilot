import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Social Autopilot',
  description: 'Automated social media promotion dashboard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}