import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export function ATSScoreBadge({ score }: { score: number | null }) {
  if (score === null) return null;

  const color =
    score >= 80
      ? "bg-green-100 text-green-800 border-green-200"
      : score >= 50
        ? "bg-yellow-100 text-yellow-800 border-yellow-200"
        : "bg-red-100 text-red-800 border-red-200";

  return (
    <Badge variant="outline" className={cn("text-xs font-mono", color)}>
      ATS {score}%
    </Badge>
  );
}
