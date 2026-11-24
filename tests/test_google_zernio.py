import json
from pathlib import Path
from PIL import Image
import api.server as server


def test_google_draft_sends_image_text_and_product_link(monkeypatch, tmp_path):
    photo = tmp_path / 'photo.jpg'
    Image.new('RGB', (600, 900), 'white').save(photo)
    monkeypatch.setenv('ZERNIO_API_KEY', 'test-key')
    monkeypatch.setenv('ZERNIO_GOOGLE_ACCOUNT_ID', 'account')
    monkeypatch.setattr(server, '_find_mission_payload', lambda _: {'results': {'image_site_1': 'photo.jpg'}})
    monkeypatch.setattr(server, '_resolve_output_relative_path', lambda _: photo)
    monkeypatch.setattr(server, 'google_post_info', lambda _: {'product_url': 'https://example.com/p/123'})
    calls = []
    class Response:
        status_code = 200
        def __init__(self, data): self.data = data
        def raise_for_status(self): pass
        def json(self): return self.data
    def post(url, **kwargs):
        calls.append((url, kwargs))
        if url.endswith('/presign'):
            return Response({'uploadUrl': 'https://upload.example.com', 'publicUrl': 'https://media.example.com/image.jpg'})
        return Response({'post': {'_id': 'draft-1', 'status': 'draft'}})
    monkeypatch.setattr(server.requests, 'post', post)
    monkeypatch.setattr(server.requests, 'put', lambda *a, **kw: Response({}))
    result = server.google_post_draft('run', {'photo': 'photo.jpg', 'content': 'Un gioiello.'})
    assert result['status'] == 'draft'
    payload = calls[-1][1]['json']
    assert payload['isDraft'] is True
    assert payload['content'] == 'Un gioiello.'
    assert payload['platforms'][0]['platformSpecificData']['callToAction']['url'] == 'https://example.com/p/123'
    assert payload['mediaItems'][0]['url'] == 'https://media.example.com/image.jpg'


def test_google_draft_rejects_unrelated_photo(monkeypatch, tmp_path):
    monkeypatch.setenv('ZERNIO_API_KEY', 'test-key')
    monkeypatch.setenv('ZERNIO_GOOGLE_ACCOUNT_ID', 'account')
    monkeypatch.setattr(server, '_find_mission_payload', lambda _: {'results': {'image_site_1': 'allowed.jpg'}})
    monkeypatch.setattr(server, 'google_post_info', lambda _: {'product_url': 'https://example.com/p/123'})
    response = server.google_post_draft('run', {'photo': '../private.jpg', 'content': 'Test'})
    assert response.status_code == 400
import asyncio
import main
import api.server as server

def test_google_text_generation_uses_product_facts(monkeypatch):
    monkeypatch.setattr(server, '_find_mission_payload', lambda _: {'results': {'analisi': 'Giacca in lana', 'publish_pack_json': '{}'}})
    monkeypatch.setattr(server, '_lab_engine', lambda _: ('', 'codex:test'))
    prompts = []
    def generate(key, model, prompt, **kwargs):
        prompts.append(prompt)
        return 'Una giacca in lana da I Monili Ravenna.'
    monkeypatch.setattr(main, 'generate_text_with_openrouter', generate)
    result = asyncio.run(server.google_generate_text('example'))
    assert 'giacca in lana' in result['text']
    assert 'Giacca in lana' in prompts[0]

def test_creative_saved_and_available_for_google(monkeypatch, tmp_path):
    from PIL import Image
    import fucina_codex
    folder = tmp_path / 'mission'
    folder.mkdir()
    manifest = folder / 'run_manifest.json'
    manifest.write_text('{}')
    source = folder / 'source.jpg'
    Image.new('RGB', (600, 900), 'white').save(source)
    monkeypatch.setattr(server, 'OUTPUT_DIR', tmp_path)
    monkeypatch.setattr(server, '_find_manifest_by_run_id', lambda _: (manifest, {}))
    monkeypatch.setattr(server, '_find_mission_payload', lambda _: {'results': {'image_site_1': 'mission/source.jpg'}})
    def generate(prompt, image, destination):
        assert image == source
        assert 'verticale 9:16' in prompt
        assert 'sfondo verde salvia' in prompt
        assert 'preservane forma' not in prompt
        destination.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB', (600, 450), 'white').save(destination)
    monkeypatch.setattr(fucina_codex, 'generate_image', generate)
    result = asyncio.run(server.google_generate_creative('test-creative', {'photo': 'mission/source.jpg', 'style': 'personalizzato', 'prompt': 'storia instagram, sfondo verde salvia, 179€'}))
    assert result['photo'] in result['creatives']
    assert result['creative_details'][result['photo']]['label'] == 'ChatGPT · Codex'
    assert server._resolve_output_relative_path(result['photo']).is_file()
    monkeypatch.setattr(server, 'STORAGE_ROOT', tmp_path)
    removed = server.google_remove_creative('test-creative', {'photo': result['photo']})
    assert result['photo'] not in removed['creatives']
    assert list((tmp_path / 'cestino' / 'creative-google').glob('*.png'))
    assert server.google_remove_creative('test-creative', {'photo': 'mission/source.jpg'}).status_code == 404
    assert 'test-creative' not in server._lab_busy

def test_flow_bridge_passes_reference_model_and_format(monkeypatch, tmp_path):
    import gflow_bridge
    from types import SimpleNamespace
    photo = tmp_path / 'pezzo.jpg'
    Image.new('RGB', (500, 500), 'white').save(photo)
    output = tmp_path / 'result.png'
    monkeypatch.setattr(gflow_bridge, 'executable', lambda: 'gflow')
    def run(command, **kwargs):
        assert command[:3] == ['gflow', 'image', 'i2i']
        assert command[command.index('--ref') + 1] == str(photo.resolve())
        assert command[command.index('--model') + 1] == 'nano2'
        assert command[command.index('--aspect') + 1] == '9:16'
        requested = Path(command[command.index('--out-file') + 1])
        Image.new('RGB', (400, 600), 'white').save(requested.with_suffix('.jpg'))
        return SimpleNamespace(returncode=0, stdout='', stderr='')
    monkeypatch.setattr(gflow_bridge.subprocess, 'run', run)
    gflow_bridge.generate_image('Una foto', photo, output, '9:16', 'nano2')
    assert output.is_file()


def test_google_creative_flow_provider(monkeypatch, tmp_path):
    import gflow_bridge
    folder = tmp_path / 'mission'
    folder.mkdir()
    manifest = folder / 'run_manifest.json'
    manifest.write_text('{}')
    source = folder / 'source.jpg'
    Image.new('RGB', (600, 900), 'white').save(source)
    monkeypatch.setattr(server, 'OUTPUT_DIR', tmp_path)
    monkeypatch.setattr(server, '_find_manifest_by_run_id', lambda _: (manifest, {}))
    monkeypatch.setattr(server, '_find_mission_payload', lambda _: {'results': {'image_site_1': 'mission/source.jpg'}})
    def generate(prompt, image, destination, aspect, model):
        assert aspect == '9:16' and model == 'nano-pro'
        assert 'sfondo verde' in prompt
        destination.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB', (400, 600), 'white').save(destination)
    monkeypatch.setattr(gflow_bridge, 'generate_image', generate)
    result = asyncio.run(server.google_generate_creative('flow-test', {'photo':'mission/source.jpg', 'style':'personalizzato', 'prompt':'sfondo verde', 'format':'story', 'provider':'flow', 'flow_model':'nano-pro'}))
    assert result['photo'] in result['creatives']
