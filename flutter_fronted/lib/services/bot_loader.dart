import 'dart:convert';
import 'package:flutter/services.dart';
import '../models/bot.dart';

class BotLoader {
  static Future<List<Bot>> loadBots() async {
    final String data = await rootBundle.loadString('assets/bots/bots.json');
    final List<dynamic> jsonResult = json.decode(data);
    return jsonResult.map((bot) => Bot.fromJson(bot)).toList();
  }
}