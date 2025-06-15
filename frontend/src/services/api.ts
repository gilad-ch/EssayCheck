
// Mock API service functions
import { toast } from "@/hooks/use-toast";

export interface EssayCheckResult {
  general_conclusion: string;
  content: {
    content_conclusion: string;
    criterias: {
      criterion: string;
      score: number;
      feedback: string;
    }[];
  };
  language: {
    language_conclusion: string;
    criterias: {
      criterion: string;
      score: number;
      feedback: string;
    }[];
  };
  suggestions: string[];
}

export interface HistoryItem {
  _id: string;
  question: string;
  essay: string;
  result: EssayCheckResult;
  date: string;
  overall_score: number;
}

export interface UserDetails {
  _id: string;
  user_id: string;
  credits: number;
}

// Mock data
const mockResult: EssayCheckResult = {
  general_conclusion: "החיבור שלך מציג רמה גבוהה מאוד של חשיבה, ארגון רעיוני וניסוח לשוני. הטיעונים מובנים היטב ומוצגים בצורה לוגית ועקבית. השפה אקדמית ומדויקת, והביטוי ברור ועשיר.",
  content: {
    content_conclusion: "הצגת עמדה ברורה, עקבית, מבוססת ומורכבת בנושא. הטיעונים מגוונים ומשכנעים, והארגון הרעיוני מעיד על חשיבה עמוקה ומובנית.",
    criterias: [
      {
        criterion: "התמקדות בנושא ואי סטייה ממנו",
        score: 6,
        feedback: "נשארת ממוקדת לכל אורך החיבור בשאלה המרכזית ולא סטית לנושאים צדדיים. כל פסקה תורמת לעמדה הכללית."
      },
      {
        criterion: "הבנת הנושא והצגת עמדה",
        score: 5,
        feedback: "הבנה עמוקה של הנושא והצגת עמדה ברורה ומנומקת. ניתן היה לחדד עוד יותר את העמדה האישית."
      },
      {
        criterion: "איכות הטיעונים והדוגמאות",
        score: 6,
        feedback: "טיעונים חזקים ומגוונים הנתמכים בדוגמאות רלוונטיות ומשכנעות מתחומי חיים שונים."
      },
      {
        criterion: "ארגון רעיוני וקוהרנטיות",
        score: 5,
        feedback: "ארגון טוב של הרעיונות עם רצף לוגי. ניתן לשפר את המעברים בין הפסקאות."
      }
    ]
  },
  language: {
    language_conclusion: "השפה שלך גבוהה, עיונית ועקבית. הביטוי ברור ומדויק, והשימוש במילים עשיר ומתאים לרמה האקדמית הנדרשת.",
    criterias: [
      {
        criterion: "דיוק בדקדוק ובתחביר",
        score: 6,
        feedback: "התחביר שלך מדויק ולא נמצאו שגיאות לשון משמעותיות. המשפטים בנויים היטב."
      },
      {
        criterion: "עושר לשוני ורמת הביטוי",
        score: 5,
        feedback: "שימוש עשיר במילים ובביטויים. הביטוי ברור ומתאים לכתיבה אקדמית."
      },
      {
        criterion: "שטף הכתיבה וקריאות הטקסט",
        score: 5,
        feedback: "הטקסט קריא ושוטף. ניתן לשפר את המעברים בין משפטים בחלק מהפסקאות."
      }
    ]
  },
  suggestions: [
    "הימנע מחזרתיות במילים ובביטויים",
    "שלב עמדות מנוגדות בצורה מורכבת יותר",
    "הקפד על ניסוח אקדמי לאורך כל החיבור",
    "חזק את המעברים בין פסקאות",
    "הוסף דוגמאות מגוונות יותר"
  ]
};

const mockHistory: HistoryItem[] = [
  {
    _id: "1",
    question: "האם הטכנולוגיה משפרת או פוגעת ביחסים החברתיים?",
    essay: "בעידן הדיגיטלי החדש...",
    result: mockResult,
    date: "2024-01-15",
    overall_score: 5.3
  },
  {
    _id: "2", 
    question: "מהי חשיבות החינוך המוסרי במערכת החינוך?",
    essay: "החינוך המוסרי הוא...",
    result: { ...mockResult, general_conclusion: "חיבור טוב עם מקום לשיפור" },
    date: "2024-01-10",
    overall_score: 4.8
  },
  {
    _id: "3",
    question: "האם יש להגביל את השימוש ברשתות החברתיות?",
    essay: "רשתות חברתיות הפכו...",
    result: { ...mockResult, general_conclusion: "חיבור מעולה עם ניתוח מעמיק" },
    date: "2024-01-05",
    overall_score: 5.7
  }
];

export const checkEssay = async (question: string, essay: string): Promise<{ essay_id: string; result: EssayCheckResult }> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  console.log("Checking essay:", { question, essay });
  
  const essay_id = Date.now().toString();
  return { essay_id, result: mockResult };
};

export const getMyHistory = async (): Promise<HistoryItem[]> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  console.log("Fetching history");
  return mockHistory;
};

export const getUserDetails = async (): Promise<UserDetails> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 300));
  
  console.log("Fetching user details");
  return {
    _id: "user_mongo_id",
    user_id: "clerk_user_id", 
    credits: 5
  };
};

export const getEssayResult = async (essayId: string): Promise<{ result: EssayCheckResult; question: string; essay: string }> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  console.log("Fetching essay result for ID:", essayId);
  
  // Find the essay in mock history or return default
  const historyItem = mockHistory.find(item => item._id === essayId);
  
  if (historyItem) {
    return {
      result: historyItem.result,
      question: historyItem.question,
      essay: historyItem.essay
    };
  }
  
  // Return default for new results
  return {
    result: mockResult,
    question: "השאלה שנבדקה",
    essay: "החיבור שנבדק"
  };
};
