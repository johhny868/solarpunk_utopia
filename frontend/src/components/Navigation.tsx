import { NavLink } from 'react-router-dom';
import {
  Home,
  Gift,
  Heart,
  ArrowLeftRight,
  Search,
  BookOpen,
  Radio,
  Bot,
  Plus,
  Users,
  MessageCircle,
  Package
} from 'lucide-react';
import { clsx } from 'clsx';
import { CommunitySelector } from './CommunitySelector';
import { usePendingCount } from '@/hooks/useAgents';

const navItems = [
  { path: '/', label: 'Home', icon: Home, tooltip: 'Dashboard and overview' },
  { path: '/offers', label: 'Offers', icon: Gift, tooltip: 'Things people are sharing' },
  { path: '/needs', label: 'Needs', icon: Heart, tooltip: 'Things people need' },
  { path: '/community-shelf', label: 'Community Shelf', icon: Package, tooltip: 'Shared community resources' },
  { path: '/exchanges', label: 'My Exchanges', icon: ArrowLeftRight, tooltip: 'Your active exchanges' },
  { path: '/cells', label: 'Local Groups', icon: Users, tooltip: 'Connect with neighbors' },
  { path: '/messages', label: 'Messages', icon: MessageCircle, tooltip: 'Direct messages' },
  { path: '/discovery', label: 'Search', icon: Search, tooltip: 'Find offers and needs' },
  { path: '/knowledge', label: 'Knowledge', icon: BookOpen, tooltip: 'Learn and share knowledge' },
  { path: '/network', label: 'Network', icon: Radio, tooltip: 'Mesh network status' },
  { path: '/agents', label: 'Smart Helpers', icon: Bot, showBadge: true, tooltip: 'AI that helps match offers with needs' },
];

export function Navigation() {
  // Poll for pending proposals count every 30 seconds using new hook
  const { data: pendingCount } = usePendingCount();

  const count = pendingCount || 0;
  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-solarpunk-400 to-solarpunk-600 rounded-lg flex items-center justify-center">
              <Gift className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Solarpunk Mesh</h1>
              <p className="text-xs text-gray-600">Gift Economy Network</p>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                title={item.tooltip}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors relative',
                    isActive
                      ? 'bg-solarpunk-100 text-solarpunk-800'
                      : 'text-gray-700 hover:bg-gray-100'
                  )
                }
              >
                <item.icon className="w-4 h-4" />
                <span>{item.label}</span>
                {item.showBadge && count > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                    {count > 9 ? '9+' : count}
                  </span>
                )}
              </NavLink>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <CommunitySelector />
            <NavLink
              to="/offers/create"
              className="flex items-center gap-2 bg-solarpunk-600 text-white px-4 py-2 rounded-lg hover:bg-solarpunk-700 transition-colors text-sm font-medium"
            >
              <Plus className="w-4 h-4" />
              <span className="hidden sm:inline">New Offer</span>
            </NavLink>
            <NavLink
              to="/needs/create"
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              <Plus className="w-4 h-4" />
              <span className="hidden sm:inline">New Need</span>
            </NavLink>
          </div>
        </div>

        {/* Mobile navigation */}
        <div className="md:hidden flex overflow-x-auto pb-3 gap-1 scrollbar-hide">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              title={item.tooltip}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap relative',
                  isActive
                    ? 'bg-solarpunk-100 text-solarpunk-800'
                    : 'text-gray-700 hover:bg-gray-100'
                )
              }
            >
              <item.icon className="w-4 h-4" />
              <span>{item.label}</span>
              {item.showBadge && count > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                  {count > 9 ? '9+' : count}
                </span>
              )}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  );
}
