import {
  createContext,
  useContext,
  useState,
} from "react";

const AuthContext = createContext(null);

const API_URL = "http://127.0.0.1:8000";

const normalizeUser = (user) => {
  if (!user) {
    return null;
  }

  const email = user.email || "";

  const gmailUsername = email
    ? email.split("@")[0]
    : "";

  const firstName =
    user.firstName ||
    user.first_name ||
    "";

  const lastName =
    user.lastName ||
    user.last_name ||
    "";

  const googleName =
    user.name ||
    user.displayName ||
    "";

  let finalFirstName = firstName;
  let finalLastName = lastName;

  if (!finalFirstName && googleName) {
    const parts = googleName
      .trim()
      .split(/\s+/);

    finalFirstName = parts[0] || "";

    if (parts.length > 1) {
      finalLastName = parts
        .slice(1)
        .join(" ");
    }
  }

  const userName =
    user.userName ||
    user.username ||
    gmailUsername;

  const isVerified =
    user.isVerified ??
    user.verified ??
    false;

  return {
    ...user,
    id:
      user.id ??
      user.user_id,
    firstName: finalFirstName,
    lastName: finalLastName,
    userName,
    email,
    name:
      googleName ||
      [finalFirstName, finalLastName]
        .filter(Boolean)
        .join(" "),
    isVerified,
    profilePhoto:
      user.profilePhoto ||
      user.profile_photo ||
      user.picture ||
      "",
  };
};

const getErrorMessage = (
  data,
  fallbackMessage
) => {
  if (!data) {
    return fallbackMessage;
  }

  if (typeof data.detail === "string") {
    return data.detail;
  }

  if (Array.isArray(data.detail)) {
    return data.detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        return (
          item.msg ||
          "Invalid request"
        );
      })
      .join(", ");
  }

  return fallbackMessage;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser =
      localStorage.getItem("user");

    if (!savedUser) {
      return null;
    }

    try {
      return normalizeUser(
        JSON.parse(savedUser)
      );
    } catch {
      localStorage.removeItem("user");
      return null;
    }
  });

  const signup = async (form) => {
    const response = await fetch(
      `${API_URL}/api/auth/register`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        getErrorMessage(
          data,
          "Registration failed"
        )
      );
    }

    return data;
  };

  const login = async (form) => {
    const response = await fetch(
      `${API_URL}/api/auth/login`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        getErrorMessage(
          data,
          "Login failed"
        )
      );
    }

    const normalizedUser =
      normalizeUser(data.user);

    localStorage.setItem(
      "access_token",
      data.access_token
    );

    localStorage.setItem(
      "user",
      JSON.stringify(normalizedUser)
    );

    setUser(normalizedUser);

    return {
      ...data,
      user: normalizedUser,
    };
  };

  const googleLogin = async (credential) => {
    const response = await fetch(
      `${API_URL}/api/auth/google`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          credential,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        getErrorMessage(
          data,
          "Google login failed"
        )
      );
    }

    const normalizedUser =
      normalizeUser(data.user);

    localStorage.setItem(
      "access_token",
      data.access_token
    );

    localStorage.setItem(
      "user",
      JSON.stringify(normalizedUser)
    );

    setUser(normalizedUser);

    return {
      ...data,
      user: normalizedUser,
    };
  };

  const sendOtp = async (phone) => {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error("Please login again.");
  }

  const response = await fetch(
    `${API_URL}/api/auth/send-otp`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        phone,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      getErrorMessage(
        data,
        "Failed to send OTP"
      )
    );
  }

  return data;
};

const resendOtp = async (phone) => {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error("Please login again.");
  }

  const response = await fetch(
    `${API_URL}/api/auth/resend-otp`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        phone,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      getErrorMessage(
        data,
        "Failed to resend OTP"
      )
    );
  }

  return data;
};

const verifyOtp = async (phone, otp) => {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error("Please login again.");
  }

  const response = await fetch(
    `${API_URL}/api/auth/verify-otp`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        phone,
        otp,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      getErrorMessage(
        data,
        "Failed to verify OTP"
      )
    );
  }

  return data;
};

  const verify = async (form) => {
    const token =
      localStorage.getItem(
        "access_token"
      );

    const response = await fetch(
      `${API_URL}/api/auth/verify`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(form),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        getErrorMessage(
          data,
          "Verification failed"
        )
      );
    }

    if (data.user) {
      const normalizedUser =
        normalizeUser(data.user);

      localStorage.setItem(
        "user",
        JSON.stringify(normalizedUser)
      );

      setUser(normalizedUser);
    }

    return data;
  };

  const updateProfile = async (form) => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      throw new Error("Please login again.");
    }

    const response = await fetch(
      `${API_URL}/api/users/me`,
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(form),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(getErrorMessage(data, "Failed to update profile"));
    }

    const normalizedUser = normalizeUser({ ...user, ...data.user });

    localStorage.setItem("user", JSON.stringify(normalizedUser));
    setUser(normalizedUser);

    return normalizedUser;
  };

  const logout = () => {
    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user"
    );

    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        signup,
        login,
        googleLogin,
        sendOtp,
        resendOtp,
        verifyOtp,
        verify,
        updateProfile,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () =>
  useContext(AuthContext);