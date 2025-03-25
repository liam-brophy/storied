import React from "react";

const LoginForm = () => {
  return (
    <div className="login-form">
      <h2>Login</h2>
      <form>
        <input type="text" placeholder="Username" name="username" />
        <input type="password" placeholder="Password" name="password" />
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default LoginForm;