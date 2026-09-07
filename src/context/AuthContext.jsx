import { createContext, useContext, useState } from "react";

// ---------------------------------------------------------------
// MOCK auth context — no backend yet. Everything lives in memory.
// When the real API is ready, replace the bodies of signup/login/
// verify/logout with actual axios calls. The pages that use
// useAuth() (SignUp, Login, Verify, Landing) will not need to change.
// ---------------------------------------------------------------

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // null = logged out

  // form -> { firstName, middleName, lastName, userName, email, password }
  const signup = (form) => {
    setUser({
      firstName: form.firstName,
      userName: form.userName,
      email: form.email,
      isVerified: false,
      profilePhoto: "",
    });
  };

  // form -> { email, password }
  const login = (form) => {
    // mock: pretend any email/password combo logs into an existing,
    // already-verified account so you can preview the verified navbar too
    setUser({
      firstName: form.email.split("@")[0] || "User",
      userName: form.email.split("@")[0] || "user",
      email: form.email,
      isVerified: true,
      profilePhoto: "",
    });
  };

  // form -> { phone, address, aadhaarNumber, otp }
  const verify = (form) => {
    setUser((prev) => ({ ...prev, ...form, isVerified: true }));
  };

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, signup, login, verify, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
