import NavBar from './components/NavBar'
import { GlobalProvider } from './functions/GlobalFunctions'

export default function App() {
  return (
    <GlobalProvider>
      <NavBar />
    </GlobalProvider>
  )
}