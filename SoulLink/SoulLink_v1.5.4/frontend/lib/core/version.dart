// lib/core/version.dart

class SoulLinkVersion {
  static const String appName = "SoulLink";
  static const String codename = "Arise";
  static const String version = "1.5.4";
  static const String build = "1";
  
  static String get displayVersion => "v$version+$build ($codename)";
  static String get fullIdentity => "$appName $codename $displayVersion";
  static String get engineTag => "LEGION ENGINE v$version";
}
