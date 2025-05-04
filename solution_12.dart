import "package:flutter/material.dart";

class SimpleCounter extends StatefulWidget {
  @override
  _SimpleCounterState createState() => _SimpleCounterState();
}

class _SimpleCounterState extends State<SimpleCounter> {
  int count = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Counter")),
      body: Center(child: Text("Count: \$count")),
      floatingActionButton: FloatingActionButton(
        onPressed: () => setState(() => count++),
        child: Icon(Icons.add),
      ),
    );
  }
}
