from gamestick_ai.read_only import scan_card


def test_scan_card_is_read_only(example):
    card,_,_=example
    before=card.db.read_bytes()
    result=scan_card(card.root)
    assert result['writes_allowed'] is False
    assert result['rom_extensions']['.nes']==1
    assert result['sqlite_databases'][0]['table_names']==['games', 'sqlite_sequence']
    assert card.db.read_bytes()==before
