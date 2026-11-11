from gamestick_ai.cli import main


def test_cli_demo_and_inspect(tmp_path,capsys):
    c=tmp_path/'sd';p=tmp_path/'package'
    assert main(['demo','--card',str(c),'--package',str(p)])==0
    assert main(['inspect','--card',str(c)])==0
    assert 'Sample Demo' in capsys.readouterr().out


def test_cli_refuses_unmarked_card(tmp_path):
    d=tmp_path/'plain';d.mkdir()
    assert main(['inspect','--card',str(d)])==2
