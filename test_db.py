from db import DB

class Test:
    
    def test_insert_order(self):
        db = DB()
        assert db.insert_notified('12345') == True
    
    def test_insert_question(self):
        db = DB()
        assert db.insert_notified('54321') == True
        
    def test_orderExists(self):
        db = DB()
        assert db.isNotified('12345') == True
        db = DB()
        assert db.isNotified('123456') == False
    