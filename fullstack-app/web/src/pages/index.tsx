import type { ReactNode } from 'react';



export function RootLayout({ children }: { children: ReactNode }): JSX.Element {
  return (
    <div className="min-h-screen bg-slate-950 text-white p-8 space-y-6"><header className="text-xl font-semibold">Nestipy Web</header>{children}</div>
  );
}


export default function Page(): JSX.Element {
  return (
    <RootLayout><div className="p-8 space-y-2"><h1>Nestipy Web</h1><p>Edit app/page.py to get started</p><a href="/user">User</a></div></RootLayout>
  );
}
