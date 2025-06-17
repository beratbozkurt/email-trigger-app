import LoginCard from '../components/LoginCard'

const LoginPage = ({ onLogin }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <LoginCard onLogin={onLogin} />
    </div>
  )
}

export default LoginPage