import { Bell, Menu, Search, User, ChevronDown, LogOut, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem,
  DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Sidebar } from './Sidebar'
import { Logo } from './Logo'
import { useAuth } from '@/store/auth'
import { useNavigate } from 'react-router-dom'

export function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="h-14 border-b bg-white dark:bg-gray-950 flex items-center justify-between px-4 md:px-6 shadow-sm sticky top-0 z-40">
      <div className="flex items-center gap-3">
        <Sheet>
          <SheetTrigger asChild className="md:hidden">
            <Button variant="ghost" size="icon"><Menu className="w-5 h-5" /></Button>
          </SheetTrigger>
          <SheetContent side="left" className="p-0 w-64"><Sidebar /></SheetContent>
        </Sheet>

        <div className="flex items-center gap-2 md:hidden">
          <Logo size={28} />
          <span className="font-bold text-[#007A5E]">DataCollect</span>
        </div>

        <div className="hidden sm:flex items-center gap-2 bg-gray-50 dark:bg-gray-900 rounded-lg px-3 py-1.5 border">
          <Search className="w-4 h-4 text-gray-400" />
          <Input
            placeholder="Rechercher..."
            className="w-56 h-7 border-0 bg-transparent p-0 text-sm focus-visible:ring-0 placeholder:text-gray-400"
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <div className="hidden md:flex gap-0.5 mr-2">
          <div className="w-1 h-5 rounded bg-[#007A5E]" />
          <div className="w-1 h-5 rounded bg-[#CE1126]" />
          <div className="w-1 h-5 rounded bg-[#FCD116]" />
        </div>

        <Button variant="ghost" size="icon" className="relative">
          <Bell className="w-4 h-4" />
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="flex items-center gap-2 h-9 px-2">
              <div className="w-7 h-7 rounded-full bg-[#007A5E] flex items-center justify-center">
                <span className="text-white text-xs font-bold">
                  {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
                </span>
              </div>
              <span className="hidden md:block text-sm max-w-[120px] truncate">
                {user?.full_name || user?.email}
              </span>
              <ChevronDown className="w-3 h-3 text-gray-400" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-52">
            <DropdownMenuLabel className="text-xs text-gray-500">
              <div>{user?.full_name || 'Utilisateur'}</div>
              <div className="font-normal text-gray-400 truncate">{user?.email}</div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => navigate('/settings')}>
              <Settings className="w-4 h-4 mr-2" />Parametres
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} className="text-red-600">
              <LogOut className="w-4 h-4 mr-2" />Deconnexion
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
