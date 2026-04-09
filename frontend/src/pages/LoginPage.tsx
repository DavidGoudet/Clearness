import { useState } from "react";
import { Navigate, useNavigate, useLocation } from "react-router-dom";
import { GoogleLogin, type CredentialResponse } from "@react-oauth/google";
import { appleAuthHelpers } from "react-apple-signin-auth";
import { useAuth } from "../hooks/useAuth";
import "./LoginPage.css";

const APPLE_CLIENT_ID = import.meta.env.VITE_APPLE_CLIENT_ID || "";

export default function LoginPage() {
  const { isAuthenticated, isLoading, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);

  const returnTo = (location.state as { from?: string })?.from || "/journal";

  if (isLoading) return <div className="loading-screen">Loading...</div>;
  if (isAuthenticated) return <Navigate to={returnTo} replace />;

  const handleGoogleSuccess = async (response: CredentialResponse) => {
    if (!response.credential) {
      setError("Sign-in failed. Please try again.");
      return;
    }

    try {
      setError(null);
      await login("google", response.credential);
      navigate(returnTo);
    } catch {
      setError("Sign-in failed. Please try again.");
    }
  };

  const handleGoogleError = () => {
    setError("Sign-in failed. Please try again.");
  };

  const handleAppleSignIn = async () => {
    try {
      setError(null);
      const response = await appleAuthHelpers.signIn({
        authOptions: {
          clientId: APPLE_CLIENT_ID,
          scope: "email name",
          redirectURI: window.location.origin,
          usePopup: true,
        },
      });

      if (!response) {
        // User cancelled the popup (AC5)
        return;
      }

      const identityToken = response.authorization.id_token;
      let userName = "";
      if (response.user?.name) {
        const { firstName, lastName } = response.user.name;
        userName = [firstName, lastName].filter(Boolean).join(" ");
      }

      await login("apple", identityToken, userName);
      navigate(returnTo);
    } catch {
      // Apple sign-in error or user cancelled
      // If user cancelled, no error is thrown by some implementations,
      // but if it is thrown, we show the error message (AC4)
      setError("Sign-in failed. Please try again.");
    }
  };

  return (
    <div className="login-page">
      <div className="login-page__logo" role="img" aria-label="Clearness logo">
        {"\uD83D\uDC8E"}
      </div>
      <h1 className="login-page__title">Clearness</h1>
      <p className="login-page__tagline">
        A few minutes of daily reflection for lasting clarity.
      </p>

      <div className="login-page__buttons">
        <div className="login-page__google-wrapper">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            type="standard"
            theme="outline"
            size="large"
            width="311"
            text="continue_with"
            shape="pill"
          />
        </div>

        <button
          className="login-page__btn login-page__btn--apple"
          onClick={handleAppleSignIn}
          aria-label="Continue with Apple"
        >
          <span className="login-page__btn--apple-icon">{"\uF8FF"}</span>
          Continue with Apple
        </button>
      </div>

      {error && (
        <p className="login-page__error" role="alert">
          {error}
        </p>
      )}

      <p className="login-page__terms">
        By continuing, you agree to our{" "}
        <a href="/terms">Terms of Service</a> and{" "}
        <a href="/privacy">Privacy Policy</a>
      </p>
    </div>
  );
}
