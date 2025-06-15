
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getEssayResult } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { ArrowRight, TrendingUp, BookOpen, MessageSquare, CheckCircle } from "lucide-react";

const Results = () => {
  const { essayId } = useParams();
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ['essayResult', essayId],
    queryFn: () => getEssayResult(essayId!),
    enabled: !!essayId
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">טוען תוצאות...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="text-gray-600 mb-4">שגיאה בטעינת התוצאות</p>
            <Button onClick={() => navigate("/")}>חזור לעמוד הבית</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { result, question, essay } = data;

  const getScoreColor = (score: number) => {
    if (score >= 5) return "text-green-600 bg-green-50";
    if (score >= 4) return "text-yellow-600 bg-yellow-50";
    return "text-red-600 bg-red-50";
  };

  const getScoreLabel = (score: number) => {
    if (score === 6) return "מעולה";
    if (score === 5) return "טוב מאוד";
    if (score === 4) return "טוב";
    if (score === 3) return "בינוני";
    if (score === 2) return "חלש";
    return "חלש מאוד";
  };

  const calculateOverallScore = () => {
    const contentScores = result.content.criterias.map(c => c.score);
    const languageScores = result.language.criterias.map(c => c.score);
    const allScores = [...contentScores, ...languageScores];
    return (allScores.reduce((sum, score) => sum + score, 0) / allScores.length).toFixed(1);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <Button 
            variant="ghost" 
            onClick={() => navigate("/")}
            className="mb-4"
          >
            <ArrowRight className="h-4 w-4 mr-2" />
            חזור לבדיקה חדשה
          </Button>
          
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-2xl">תוצאות הבדיקה</CardTitle>
                  <CardDescription className="mt-2 text-right">
                    {question}
                  </CardDescription>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {calculateOverallScore()}
                  </div>
                  <p className="text-sm text-gray-500">ציון כללי</p>
                </div>
              </div>
            </CardHeader>
          </Card>
        </div>

        {/* General Conclusion */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <MessageSquare className="h-5 w-5 ml-2" />
              מסקנה כללית
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 leading-relaxed text-right">
              {result.general_conclusion}
            </p>
          </CardContent>
        </Card>

        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Content Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BookOpen className="h-5 w-5 ml-2" />
                תוכן
              </CardTitle>
              <CardDescription className="text-right">
                {result.content.content_conclusion}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {result.content.criterias.map((criteria, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Badge className={getScoreColor(criteria.score)}>
                        {criteria.score}/6 - {getScoreLabel(criteria.score)}
                      </Badge>
                    </div>
                    <h4 className="font-semibold text-right mb-2">
                      {criteria.criterion}
                    </h4>
                    <Progress value={(criteria.score / 6) * 100} className="mb-2" />
                    <p className="text-sm text-gray-600 text-right">
                      {criteria.feedback}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Language Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <MessageSquare className="h-5 w-5 ml-2" />
                שפה
              </CardTitle>
              <CardDescription className="text-right">
                {result.language.language_conclusion}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {result.language.criterias.map((criteria, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Badge className={getScoreColor(criteria.score)}>
                        {criteria.score}/6 - {getScoreLabel(criteria.score)}
                      </Badge>
                    </div>
                    <h4 className="font-semibold text-right mb-2">
                      {criteria.criterion}
                    </h4>
                    <Progress value={(criteria.score / 6) * 100} className="mb-2" />
                    <p className="text-sm text-gray-600 text-right">
                      {criteria.feedback}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Suggestions */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 ml-2" />
              המלצות לשיפור
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              {result.suggestions.map((suggestion, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-gray-700 text-right">
                    {suggestion}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-center space-x-4">
          <Button onClick={() => navigate("/")}>
            בדוק חיבור נוסף
          </Button>
          <Button variant="outline" onClick={() => navigate("/history")}>
            צפה בהיסטוריה
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Results;
