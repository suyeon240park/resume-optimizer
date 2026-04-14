"use client";

import { useRouter } from "next/navigation";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "@/lib/auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();

  return (
    <div className="flex items-center justify-center min-h-screen bg-muted/30">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Resume Optimizer</CardTitle>
          <p className="text-muted-foreground text-sm mt-1">
            Tailor your LaTeX resume to any job description
          </p>
        </CardHeader>
        <CardContent className="flex justify-center">
          <GoogleLogin
            onSuccess={async (response) => {
              if (response.credential) {
                await login(response.credential);
                router.push("/dashboard");
              }
            }}
            onError={() => {
              console.error("Google login failed");
            }}
          />
        </CardContent>
      </Card>
    </div>
  );
}
