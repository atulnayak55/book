import type { ReactNode } from "react";

type MainLayoutProps = {
  children: ReactNode;
};

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <p className="app-kicker">UniPd Marketplace</p>
        <h1>Book Listings</h1>
        <p className="app-subtitle">
          Browse books by department, program, and course.
        </p>
      </header>
      <main className="app-content">{children}</main>
    </div>
  );
}
