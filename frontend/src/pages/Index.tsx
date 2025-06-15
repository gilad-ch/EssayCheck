
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { SignedIn, SignedOut, SignInButton } from "@clerk/clerk-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useQuery } from "@tanstack/react-query";
import { checkEssay, getUserDetails } from "@/services/api";
import { toast } from "@/hooks/use-toast";
import { CheckCircle, Users, Clock, Award, ChevronDown } from "lucide-react";

const Index = () => {
  const [question, setQuestion] = useState("");
  const [essay, setEssay] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const { data: userDetails } = useQuery({
    queryKey: ['userDetails'],
    queryFn: getUserDetails,
    enabled: true // Will only work when signed in due to Clerk
  });

  const handleSubmit = async () => {
    if (!question.trim() || !essay.trim()) {
      toast({
        title: "שגיאה",
        description: "יש למלא את שדה השאלה ואת שדה החיבור",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await checkEssay(question, essay);
      navigate(`/results/${result.essay_id}`);
      toast({
        title: "הבדיקה הושלמה!",
        description: "החיבור שלך נבדק בהצלחה"
      });
    } catch (error) {
      toast({
        title: "שגיאה",
        description: "אירעה שגיאה בבדיקת החיבור. נסה שוב.",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const scrollToForm = () => {
    document.getElementById('essay-form')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
            בדוק את החיבור שלך בחינם,<br />
            <span className="text-blue-600">ברמה של מעריך אנושי</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            מערכת אוטומטית לבדיקת חיבורים לפי קריטריוני המרכז הארצי לבחינות והערכה
          </p>
        </div>

        {/* Credits indicator for signed-in users */}
        <SignedIn>
          <div className="mb-8">
            {userDetails && (
              <Badge variant="secondary" className="text-lg px-4 py-2">
                נותרו לך {userDetails.credits} בדיקות בחינם
              </Badge>
            )}
          </div>
        </SignedIn>

        {/* Essay Form */}
        <Card id="essay-form" className="text-right max-w-4xl mx-auto mb-12">
          <CardHeader>
            <CardTitle className="text-2xl">בדיקת החיבור שלך</CardTitle>
            <CardDescription>
              הכנס את השאלה ואת החיבור שלך לקבלת משב נפורט ומקצועי
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                השאלה
              </label>
              <Textarea
                placeholder="הקלד כאן את השאלה או הדבק טקסט"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="min-h-[100px] text-right"
                dir="rtl"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                החיבור שלך
              </label>
              <Textarea
                placeholder="הקלד כאן את החיבור שלך או הדבק טקסט"
                value={essay}
                onChange={(e) => setEssay(e.target.value)}
                className="min-h-[300px] text-right"
                dir="rtl"
              />
            </div>

            <SignedIn>
              <Button 
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="w-full text-lg py-6"
                size="lg"
              >
                {isSubmitting ? "בודק את החיבור..." : "בדוק את החיבור שלי"}
              </Button>
            </SignedIn>

            <SignedOut>
              <SignInButton mode="modal">
                <Button className="w-full text-lg py-6" size="lg">
                  התחבר כדי לבדוק את החיבור
                </Button>
              </SignInButton>
              <p className="text-sm text-gray-500 mt-2">
                נדרשת הרשמה חינמית לשימוש במערכת
              </p>
            </SignedOut>
          </CardContent>
        </Card>

        {/* Scroll indicator */}
        <button 
          onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
          className="animate-bounce"
        >
          <ChevronDown className="h-8 w-8 text-gray-400 mx-auto" />
        </button>
      </div>

      {/* Features Section */}
      <div id="features" className="bg-white py-16">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            למה לבחור בנו?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center">
              <CardHeader>
                <Award className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <CardTitle>בדיקה מקצועית</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  בדיקה מפורטת לפי קריטריוני המרכז הארצי עם ציונים מדויקים לכל תחום
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Clock className="h-12 w-12 text-green-600 mx-auto mb-4" />
                <CardTitle>תוצאות מיידיות</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  קבל משוב מפורט תוך שניות ספורות במקום להמתין שבועות
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Users className="h-12 w-12 text-purple-600 mx-auto mb-4" />
                <CardTitle>מעקב התקדמות</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  עקוב אחר ההתקדמות שלך לאורך זמן וזהה תחומים לשיפור
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* How it works */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-12">איך זה עובד?</h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="flex flex-col items-center">
              <div className="bg-blue-100 rounded-full p-4 mb-4">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">הכנס את החיבור</h3>
              <p className="text-gray-600">העלה את השאלה ואת החיבור שלך</p>
            </div>

            <div className="flex flex-col items-center">
              <div className="bg-green-100 rounded-full p-4 mb-4">
                <span className="text-2xl font-bold text-green-600">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">בדיקה אוטומטית</h3>
              <p className="text-gray-600">המערכת בודקת את החיבור לפי קריטריוני המרכז הארצי</p>
            </div>

            <div className="flex flex-col items-center">
              <div className="bg-purple-100 rounded-full p-4 mb-4">
                <span className="text-2xl font-bold text-purple-600">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">קבל משוב מפורט</h3>
              <p className="text-gray-600">צפה בציונים, הערות והמלצות לשיפור</p>
            </div>
          </div>
        </div>
      </div>

      {/* FAQ */}
      <div className="bg-white py-16">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">שאלות נפוצות</h2>
          
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-right">איך המערכת יודעת לבדוק חיבורים?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-right">
                  המערכת מבוססת על בינה מלאכותית שאומנה על אלפי חיבורים שנבדקו על ידי מעריכים מקצועיים. 
                  היא בודקת את החיבור לפי הקריטריונים הרשמיים של המרכז הארצי לבחינות והערכה.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-right">כמה זמן לוקחת הבדיקה?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-right">
                  הבדיקה מתבצעת תוך שניות ספורות. תקבל משוב מיידי ומפורט על החיבור שלך.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-right">האם המערכת שומרת את החיבורים שלי?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-right">
                  כן, המערכת שומרת את החיבורים שלך כדי שתוכל לעקוב אחר ההתקדמות שלך לאורך זמן. 
                  המידע מאובטח ונשמר בפרטיות מלאה.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="bg-blue-600 py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">מוכן להתחיל?</h2>
          <p className="text-xl text-blue-100 mb-8">
            הצטרף לאלפי תלמידים שכבר משפרים את כישורי הכתיבה שלהם
          </p>
          <Button 
            onClick={scrollToForm}
            size="lg" 
            variant="secondary"
            className="text-lg px-8 py-4"
          >
            התחילו עכשיו
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Index;
