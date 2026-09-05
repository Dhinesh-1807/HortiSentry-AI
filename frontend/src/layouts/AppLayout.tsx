import React from 'react';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { HealthStatus, UserRole, AuthUser } from '../types';

interface AppLayoutProps {
  children: React.ReactNode;
  currentRole: UserRole;
  currentRoute: string;
  onNavigate: (route: string) => void;
  onSelectRole: (role: UserRole) => void;
  health: HealthStatus | null;
  user: AuthUser | null;
  onLogout: () => void;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  children,
  currentRole,
  currentRoute,
  onNavigate,
  onSelectRole,
  health,
  user,
  onLogout
}) => {
  return (
    <div className="min-h-screen flex flex-col bg-[#F8FAF8] text-[#1F2937] font-sans antialiased">
      <Navbar
        currentRole={currentRole}
        currentRoute={currentRoute}
        onNavigate={onNavigate}
        onSelectRole={onSelectRole}
        health={health}
        user={user}
        onLogout={onLogout}
      />
      
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>

      <Footer onNavigate={onNavigate} />
    </div>
  );
};
