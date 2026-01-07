class AuthService {
  Future<void> loginWithEmail(String email, String password) async {
    // TEMP: skip auth
    print("Mock email login: $email");
  }

  Future<void> loginWithGoogle() async {
    // TEMP: skip auth
    print("Mock Google login");
  }

  Future<void> loginAsGuest() async {
    // TEMP: guest mode
    print("Mock guest login");
  }
}
