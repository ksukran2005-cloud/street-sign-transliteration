import 'package:flutter_test/flutter_test.dart';
import 'package:street_sign_app/main.dart';

void main() {
  testWidgets('Street Sign Translator launches', (WidgetTester tester) async {
    await tester.pumpWidget(const StreetSignApp());

    expect(find.text('Street Sign Translator'), findsOneWidget);
    expect(find.text('Understand every sign.'), findsOneWidget);
    expect(find.text('Gallery'), findsOneWidget);
    expect(find.text('Camera'), findsOneWidget);
  });
}