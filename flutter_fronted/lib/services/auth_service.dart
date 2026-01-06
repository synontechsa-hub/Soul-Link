import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';

class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;

  // Email login
  Future<UserCredential> loginWithEmail(String email, String password) {
    return _auth.signInWithEmailAndPassword(email: email, password: password);
  }

  // Guest login
  Future<UserCredential> loginAsGuest() {
    return _auth.signInAnonymously();
  }

  // Google login
  Future<UserCredential> loginWithGoogle() async {
    final GoogleSignInAccount? googleUser = await GoogleSignIn().signIn();
    final GoogleSignInAuthentication googleAuth = await googleUser!.authentication;
    final credential = GoogleAuthProvider.credential(
      accessToken: googleAuth.accessToken,
      idToken: googleAuth.idToken,
    );
    return _auth.signInWithCredential(credential);
  }

  // Link guest to email/social
  Future<UserCredential> linkAccount(AuthCredential credential) {
    return _auth.currentUser!.linkWithCredential(credential);
  }

  // Logout
  Future<void> logout() => _auth.signOut();
}