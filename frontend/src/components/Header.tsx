
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/clerk-react";
import { Button } from "@/components/ui/button";
import { useNavigate, useLocation } from "react-router-dom";
import { History, Home, PenTool } from "lucide-react";

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and brand */}
          <div className="flex items-center">
            <button 
              onClick={() => navigate("/")}
              className="flex items-center space-x-2 hover:opacity-80 transition-opacity"
            >
              <PenTool className="h-8 w-8 text-blue-600" />
              <div className="text-right">
                <h1 className="text-xl font-bold text-gray-900">בדיקת חיבורים</h1>
                <p className="text-xs text-gray-500">מערכת בדיקה אוטומטית</p>
              </div>
            </button>
          </div>

          {/* Navigation */}
          <div className="flex items-center space-x-4">
            <SignedIn>
              <Button
                variant={location.pathname === "/" ? "default" : "ghost"}
                onClick={() => navigate("/")}
                className="flex items-center space-x-2"
              >
                <Home className="h-4 w-4" />
                <span>בדיקה חדשה</span>
              </Button>
              
              <Button
                variant={location.pathname === "/history" ? "default" : "ghost"}
                onClick={() => navigate("/history")}
                className="flex items-center space-x-2"
              >
                <History className="h-4 w-4" />
                <span>היסטוריה</span>
              </Button>
              
              <UserButton 
                appearance={{
                  elements: {
                    avatarBox: "w-8 h-8"
                  }
                }}
              />
            </SignedIn>
            
            <SignedOut>
              <SignInButton mode="modal">
                <Button variant="default">
                  התחברות
                </Button>
              </SignInButton>
            </SignedOut>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
