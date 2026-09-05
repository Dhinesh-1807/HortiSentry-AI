import React, { useEffect, useState } from 'react';
import { AppLayout } from './layouts/AppLayout';
import { ErrorBoundary } from './components/ErrorBoundary';

// Public Pages
import { LandingPage } from './pages/public/LandingPage';
import { AboutPage } from './pages/public/AboutPage';
import { HowItWorksPage } from './pages/public/HowItWorksPage';
import { LoginPage } from './pages/public/LoginPage';
import { RegisterPage } from './pages/public/RegisterPage';

// Farmer Pages
import { FarmerHome } from './pages/farmer/FarmerHome';
import { ObservationWizard } from './pages/farmer/ObservationWizard';
import { ObservationResult } from './pages/farmer/ObservationResult';
import { AIReviewDetail } from './pages/farmer/AIReviewDetail';
import { ObservationHistory } from './pages/farmer/ObservationHistory';
import { ObservationDetail } from './pages/farmer/ObservationDetail';
import { ExpertReviewStatus } from './pages/farmer/ExpertReviewStatus';
import { FarmerProfile } from './pages/farmer/FarmerProfile';

// Expert Pages
import { ExpertHome } from './pages/expert/ExpertHome';
import { ReviewQueue } from './pages/expert/ReviewQueue';
import { CaseDetail } from './pages/expert/CaseDetail';
import { ReviewHistory } from './pages/expert/ReviewHistory';
import { ExpertProfile } from './pages/expert/ExpertProfile';
import { ExpertStatusPage } from './pages/expert/ExpertStatusPage';

// Admin Pages
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { UserManagement } from './pages/admin/UserManagement';
import { CropManagement } from './pages/admin/CropManagement';
import { AdminAnalytics } from './pages/admin/AdminAnalytics';
import { ModelDatasetInfo } from './pages/admin/ModelDatasetInfo';
import { AuditLogViewer } from './pages/admin/AuditLogViewer';

// Shared Components & Services
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorPage } from './components/ErrorPage';
import { fetchHealth, fetchCrops, authGetMe, authDemoLogin, clearAuthToken } from './services/api';
import { HealthStatus, CropConfig, UserRole, AuthUser } from './types';

export const App: React.FC = () => {
  const [currentRole, setCurrentRole] = useState<UserRole>('public');
  const [currentRoute, setCurrentRoute] = useState<string>('/');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [crops, setCrops] = useState<CropConfig[]>([]);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadInitialData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthData, cropsData] = await Promise.all([
        fetchHealth().catch(() => ({
          status: 'ok',
          environment: 'production',
          model_loaded: true,
          model_name: 'MobileNetV3-Small-HortiSentry',
          num_classes: 10,
          ml_mode: 'DEMO',
          database_connected: true
        } as HealthStatus)),
        fetchCrops().catch(() => [])
      ]);
      setHealth(healthData);
      setCrops(cropsData);

      // Attempt to load active session if token stored
      try {
        const me = await authGetMe();
        if (me && me.user) {
          setUser(me.user);
          const role = (me.user.role || '').toLowerCase();
          setCurrentRole(role as UserRole);

          const vStatus = (me.user.verification_status || 'NOT_REQUIRED').toUpperCase();
          const aStatus = (me.user.account_status || 'ACTIVE').toUpperCase();
          if (role === 'expert' && (vStatus !== 'VERIFIED' || aStatus === 'SUSPENDED')) {
            if (window.location.pathname.startsWith('/expert') || currentRoute.startsWith('/expert')) {
              setCurrentRoute('/expert/status');
            }
          }
        }
      } catch {
        // No saved token; stay on public
      }
    } catch (err: any) {
      console.error('Error loading initial HortiSentry data:', err);
      setError(err.message || 'Failed to communicate with HortiSentry backend');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const navigate = (route: string) => {
    const userRole = (user?.role || '').toLowerCase();
    const vStatus = (user?.verification_status || 'NOT_REQUIRED').toUpperCase();
    const aStatus = (user?.account_status || 'ACTIVE').toUpperCase();

    // Guard Expert Routes
    if (route.startsWith('/expert')) {
      if (!user) {
        setCurrentRoute('/login');
        window.scrollTo(0, 0);
        return;
      }
      if (userRole !== 'expert') {
        setCurrentRoute('/farmer');
        window.scrollTo(0, 0);
        return;
      }
      // If expert is not VERIFIED or is SUSPENDED, force /expert/status
      if ((vStatus !== 'VERIFIED' || aStatus === 'SUSPENDED') && route !== '/expert/status') {
        setCurrentRoute('/expert/status');
        window.scrollTo(0, 0);
        return;
      }
    }

    // Guard Admin Routes
    if (route.startsWith('/admin')) {
      if (!user || userRole !== 'admin') {
        setCurrentRoute('/login');
        window.scrollTo(0, 0);
        return;
      }
    }

    setCurrentRoute(route);

    // Auto-align role with route namespace
    if (route.startsWith('/farmer')) {
      setCurrentRole('farmer');
    } else if (route.startsWith('/expert')) {
      setCurrentRole('expert');
    } else if (route.startsWith('/admin')) {
      setCurrentRole('admin');
    } else if (route === '/' || route === '/about' || route === '/how-it-works' || route === '/login' || route === '/register') {
      if (!user) setCurrentRole('public');
    }
    window.scrollTo(0, 0);
  };

  useEffect(() => {
    (window as any).hortisentryNavigate = (route: string) => navigate(route);
    (window as any).hortisentryLogout = handleLogout;
  }, [user]);

  const handleSelectRole = (role: UserRole) => {
    setCurrentRole(role);
    if (role === 'farmer') setCurrentRoute('/farmer');
    else if (role === 'expert') {
      const vStatus = (user?.verification_status || 'NOT_REQUIRED').toUpperCase();
      const aStatus = (user?.account_status || 'ACTIVE').toUpperCase();
      if (user?.role === 'expert' && (vStatus !== 'VERIFIED' || aStatus === 'SUSPENDED')) {
        setCurrentRoute('/expert/status');
      } else {
        setCurrentRoute('/expert');
      }
    }
    else if (role === 'admin') setCurrentRoute('/admin');
    else setCurrentRoute('/');
    window.scrollTo(0, 0);
  };

  const handleLoginSuccess = (authUser: AuthUser) => {
    setUser(authUser);
    const role = (authUser.role || '').toLowerCase();
    const vStatus = (authUser.verification_status || 'NOT_REQUIRED').toUpperCase();
    const aStatus = (authUser.account_status || 'ACTIVE').toUpperCase();

    if (role === 'admin') {
      setCurrentRole('admin');
      setCurrentRoute('/admin');
    } else if (role === 'expert') {
      setCurrentRole('expert');
      if (vStatus === 'VERIFIED' && aStatus === 'ACTIVE') {
        setCurrentRoute('/expert');
      } else {
        setCurrentRoute('/expert/status');
      }
    } else {
      setCurrentRole('farmer');
      setCurrentRoute('/farmer');
    }
    window.scrollTo(0, 0);
  };

  const handleLogout = () => {
    clearAuthToken();
    setUser(null);
    setCurrentRole('public');
    setCurrentRoute('/');
  };

  const isExpertUnverified =
    (user?.role || '').toLowerCase() === 'expert' &&
    ((user?.verification_status || '').toUpperCase() !== 'VERIFIED' ||
      (user?.account_status || '').toUpperCase() === 'SUSPENDED');

  if (loading) {
    return <LoadingSpinner message="Initializing HortiSentry surveillance platform..." />;
  }

  if (error && !health) {
    return <ErrorPage message={error} onRetry={loadInitialData} />;
  }

  return (
    <AppLayout
      currentRole={currentRole}
      currentRoute={currentRoute}
      onNavigate={navigate}
      onSelectRole={handleSelectRole}
      health={health}
      user={user}
      onLogout={handleLogout}
    >
      <ErrorBoundary onReset={() => navigate('/')}>
        {/* PUBLIC ROUTES */}
        {currentRoute === '/' && (
          <LandingPage
            health={health}
            crops={crops}
            onNavigate={navigate}
          />
        )}
        {currentRoute === '/about' && <AboutPage onNavigate={navigate} />}
        {currentRoute === '/how-it-works' && <HowItWorksPage onNavigate={navigate} />}
        {currentRoute.startsWith('/login') && (
          <LoginPage onNavigate={navigate} onLoginSuccess={handleLoginSuccess} />
        )}
        {currentRoute.startsWith('/register') && (
          <RegisterPage onNavigate={navigate} onRegisterSuccess={handleLoginSuccess} />
        )}

        {/* FARMER ROUTES */}
        {currentRoute === '/farmer' && (
          <FarmerHome crops={crops} onNavigate={navigate} />
        )}
        {currentRoute === '/farmer/observation/new' && (
          <ObservationWizard crops={crops} onNavigate={navigate} />
        )}
        {(currentRoute === '/farmer/observations' || currentRoute === '/farmer/history') && (
          <ObservationHistory onNavigate={navigate} />
        )}
        {currentRoute.startsWith('/farmer/observations/') && (
          <ObservationDetail
            observationId={currentRoute.replace('/farmer/observations/', '')}
            onNavigate={navigate}
          />
        )}
        {currentRoute.startsWith('/farmer/result/') && (
          <ObservationResult
            observationId={currentRoute.replace('/farmer/result/', '')}
            onNavigate={navigate}
          />
        )}
        {currentRoute.startsWith('/ai-review/') && (
          <AIReviewDetail
            observationId={currentRoute.replace('/ai-review/', '')}
            onNavigate={navigate}
          />
        )}
        {currentRoute.startsWith('/farmer/reviews/') && (
          <ExpertReviewStatus
            observationId={currentRoute.replace('/farmer/reviews/', '')}
            onNavigate={navigate}
          />
        )}
        {currentRoute === '/farmer/profile' && (
          <FarmerProfile user={user} onNavigate={navigate} />
        )}

        {/* EXPERT ROUTES */}
        {currentRoute === '/expert/status' && (
          <ExpertStatusPage user={user} onNavigate={navigate} onLogout={handleLogout} />
        )}
        {currentRoute === '/expert' && (
          isExpertUnverified ? (
            <ExpertStatusPage user={user} onNavigate={navigate} onLogout={handleLogout} />
          ) : (
            <ExpertHome onNavigate={navigate} />
          )
        )}
        {(currentRoute === '/expert/queue' || currentRoute === '/expert/cases' || currentRoute === '/expert/reviews') && (
          isExpertUnverified ? (
            <ExpertStatusPage user={user} onNavigate={navigate} onLogout={handleLogout} />
          ) : (
            <ReviewQueue onNavigate={navigate} />
          )
        )}
        {(currentRoute.startsWith('/expert/cases/') || currentRoute.startsWith('/expert/reviews/')) && (
          isExpertUnverified ? (
            <ExpertStatusPage user={user} onNavigate={navigate} onLogout={handleLogout} />
          ) : (
            <CaseDetail
              reviewId={currentRoute.replace('/expert/cases/', '').replace('/expert/reviews/', '')}
              onNavigate={navigate}
            />
          )
        )}
        {currentRoute === '/expert/history' && (
          isExpertUnverified ? (
            <ExpertStatusPage user={user} onNavigate={navigate} onLogout={handleLogout} />
          ) : (
            <ReviewHistory onNavigate={navigate} />
          )
        )}
        {currentRoute === '/expert/profile' && (
          <ExpertProfile user={user} onNavigate={navigate} />
        )}

        {/* ADMIN ROUTES */}
        {currentRoute === '/admin' && (
          <AdminDashboard onNavigate={navigate} />
        )}
        {currentRoute === '/admin/users' && (
          <UserManagement onNavigate={navigate} />
        )}
        {currentRoute === '/admin/crops' && (
          <CropManagement onNavigate={navigate} />
        )}
        {currentRoute === '/admin/analytics' && (
          <AdminAnalytics onNavigate={navigate} />
        )}
        {currentRoute === '/admin/model' && (
          <ModelDatasetInfo onNavigate={navigate} />
        )}
        {currentRoute === '/admin/audit-logs' && (
          <AuditLogViewer onNavigate={navigate} />
        )}
      </ErrorBoundary>
    </AppLayout>
  );
};

export default App;
