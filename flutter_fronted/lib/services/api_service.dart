import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/bot.dart';

class ApiService {
  static const String baseUrl = "http://localhost:5000"; // replace with your backend URL

  static Future<String> sendMessage(Bot bot, String message) async {
    final response = await http.post(
      Uri.parse("$baseUrl/chat"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "bot": bot.name,
        "message": message,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data["reply"] ?? "No response";
    } else {
      return "Error: ${response.statusCode}";
    }
  }
}