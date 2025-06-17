import { useLocation, Link } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'

const Breadcrumb = () => {
  const location = useLocation()
  const pathnames = location.pathname.split('/').filter((x) => x)

  const routeNames = {
    dashboard: 'Dashboard',
    emails: 'Emails',
    triggers: 'Triggers',
    settings: 'Settings',
    login: 'Login'
  }

  // Don't show breadcrumb on dashboard home
  if (location.pathname === '/dashboard') {
    return null
  }

  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
      <Link to="/dashboard" className="flex items-center hover:text-gray-700">
        <Home className="w-4 h-4" />
      </Link>
      
      {pathnames.map((pathname, index) => {
        const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`
        const isLast = index === pathnames.length - 1
        const displayName = routeNames[pathname] || pathname.charAt(0).toUpperCase() + pathname.slice(1)

        return (
          <div key={pathname} className="flex items-center">
            <ChevronRight className="w-4 h-4 mx-2" />
            {isLast ? (
              <span className="text-gray-900 font-medium">{displayName}</span>
            ) : (
              <Link 
                to={routeTo} 
                className="hover:text-gray-700"
              >
                {displayName}
              </Link>
            )}
          </div>
        )
      })}
    </nav>
  )
}

export default Breadcrumb