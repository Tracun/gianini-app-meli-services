from db import DB

class Test:
    
    def test_insert_order(self):
        db = DB()
        assert db.insert_notified('12345', 'orders') == True
    
    def test_insert_question(self):
        db = DB()
        assert db.insert_notified('12345', 'questions') == True
        
    def test_orderExists(self):
        db = DB()
        assert db.isNotified('12345', 'orders') == True
        db = DB()
        assert db.isNotified('123456', 'orders') == False
    
    def test_questionExists(self):
        db = DB()
        assert db.isNotified('12345', 'questions') == True
        db = DB()
        assert db.isNotified('123456', 'questions') == False