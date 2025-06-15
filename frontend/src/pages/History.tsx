
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getMyHistory } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ArrowRight, TrendingUp, TrendingDown, Minus, Calendar, FileText, BarChart3 } from "lucide-react";

const History = () => {
  const navigate = useNavigate();

  const { data: history, isLoading, error } = useQuery({
    queryKey: ['history'],
    queryFn: getMyHistory
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">טוען היסטוריה...</p>
        </div>
      </div>
    );
  }

  if (error || !history) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="text-gray-600 mb-4">שגיאה בטעינת ההיסטוריה</p>
            <Button onClick={() => navigate("/")}>חזור לעמוד הבית</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const calculateStats = () => {
    if (history.length === 0) return { totalEssays: 0, averageScore: 0, bestScore: 0, trend: "none" };
    
    const scores = history.map(item => item.overall_score);
    const totalEssays = history.length;
    const averageScore = (scores.reduce((sum, score) => sum + score, 0) / totalEssays).toFixed(1);
    const bestScore = Math.max(...scores).toFixed(1);
    
    // Calculate trend - compare last 3 vs first 3 essays
    let trend = "none";
    if (totalEssays >= 3) {
      const recent = scores.slice(-3);
      const older = scores.slice(0, 3);
      const recentAvg = recent.reduce((sum, score) => sum + score, 0) / recent.length;
      const olderAvg = older.reduce((sum, score) => sum + score, 0) / older.length;
      
      if (recentAvg > olderAvg + 0.2) trend = "up";
      else if (recentAvg < olderAvg - 0.2) trend = "down";
    }
    
    return { totalEssays, averageScore, bestScore, trend };
  };

  const getTrendIcon = (currentScore: number, previousScore: number | null) => {
    if (!previousScore) return <Minus className="h-4 w-4 text-gray-400" />;
    
    if (currentScore > previousScore) return <TrendingUp className="h-4 w-4 text-green-600" />;
    if (currentScore < previousScore) return <TrendingDown className="h-4 w-4 text-red-600" />;
    return <Minus className="h-4 w-4 text-gray-400" />;
  };

  const getScoreColor = (score: number) => {
    if (score >= 5) return "bg-green-100 text-green-800";
    if (score >= 4) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('he-IL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const stats = calculateStats();

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
            חזור לעמוד הבית
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-6 text-right">היסטוריית החיבורים שלי</h1>
          
          {/* Statistics Cards */}
          <div className="grid md:grid-cols-4 gap-4 mb-8">
            <Card>
              <CardContent className="p-6 text-center">
                <FileText className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">{stats.totalEssays}</div>
                <p className="text-sm text-gray-600">חיבורים נבדקו</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <BarChart3 className="h-8 w-8 text-green-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">{stats.averageScore}</div>
                <p className="text-sm text-gray-600">ממוצע כללי</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <TrendingUp className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">{stats.bestScore}</div>
                <p className="text-sm text-gray-600">הציון הטוב ביותר</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                {stats.trend === "up" && <TrendingUp className="h-8 w-8 text-green-600 mx-auto mb-2" />}
                {stats.trend === "down" && <TrendingDown className="h-8 w-8 text-red-600 mx-auto mb-2" />}
                {stats.trend === "none" && <Minus className="h-8 w-8 text-gray-400 mx-auto mb-2" />}
                <div className="text-sm font-semibold text-gray-900">
                  {stats.trend === "up" && "מגמת עלייה"}
                  {stats.trend === "down" && "מגמת ירידה"}
                  {stats.trend === "none" && "ללא מגמה"}
                </div>
                <p className="text-sm text-gray-600">מגמה כללית</p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* History Table */}
        {history.length === 0 ? (
          <Card>
            <CardContent className="py-16 text-center">
              <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">אין עדיין חיבורים</h3>
              <p className="text-gray-600 mb-6">התחל לבדוק חיבורים כדי לראות את ההיסטוריה כאן</p>
              <Button onClick={() => navigate("/")}>
                בדוק חיבור ראשון
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="h-5 w-5 ml-2" />
                רשימת החיבורים
              </CardTitle>
              <CardDescription>
                לחץ על כל שורה כדי לצפות בפירוט התוצאות
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-right">תאריך</TableHead>
                    <TableHead className="text-right">השאלה</TableHead>
                    <TableHead className="text-right">ציון כללי</TableHead>
                    <TableHead className="text-right">מגמה</TableHead>
                    <TableHead className="text-right">פעולות</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {history.map((item, index) => {
                    const previousScore = index < history.length - 1 ? history[index + 1].overall_score : null;
                    return (
                      <TableRow 
                        key={item._id}
                        className="cursor-pointer hover:bg-gray-50"
                        onClick={() => navigate(`/results/${item._id}`)}
                      >
                        <TableCell className="text-right">
                          {formatDate(item.date)}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="max-w-xs truncate">
                            {item.question}
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <Badge className={getScoreColor(item.overall_score)}>
                            {item.overall_score.toFixed(1)}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          {getTrendIcon(item.overall_score, previousScore)}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/results/${item._id}`);
                            }}
                          >
                            צפה בפירוט
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="mt-8 text-center">
          <Button onClick={() => navigate("/")} size="lg">
            בדוק חיבור חדש
          </Button>
        </div>
      </div>
    </div>
  );
};

export default History;
