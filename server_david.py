import flask
from flask import Flask, render_template, redirect, request, url_for, session, flash
from youtube_dl import YoutubeDL
from flask_http2_push import http2push
import time


app = Flask(__name__, template_folder='templates')


def get_time():
    return str(hash(str(time.time())))


def extract_url(youtube_id):
    ydl = YoutubeDL()
    ydl.add_default_info_extractors()
    weburl = 'https://www.youtube.com/watch?v=' + youtube_id
    info = ydl.extract_info(weburl, download=False)
    resolution = {
        '133': '240',
        '134': '360',
        '135': '480',
        '136': '720',
        '137': '1080',
        '160': '144',
        '278': '144',
        '242': '240',
        '243': '360',
        '244': '480',
        '247': '720',
        '248': '1080'
    }
    video_type = {
        '133': 'video/mp4', '134': 'video/mp4', '135': 'video/mp4', '136': 'video/mp4',
        '137': 'video/mp4', '18': 'video/mp4', '22': 'video/mp4',
        '160': 'video/mp4',
        '278': 'video/webm', '242': 'video/webm', '243': 'video/webm', '244': 'video/webm',
        '247': 'video/webm', '248': 'video/webm'
    }
    audio_list = ['139', '140', '141', '256', '258', '325', '328', '171', '172', '249', '250', '251']
    audio_type = {
        '139': 'audio/m4a', '140': 'audio/m4a', '141': 'audio/m4a', '256': 'audio/m4a',
        '258': 'audio/m4a', '325': 'audio/m4a', '328': 'audio/m4a',
        '171': 'audio/webm', '172': 'audio/webm', '249': 'audio/webm',
        '250': 'audio/webm', '251': 'audio/webm'
    }

    quote = "\""
    first_video = True
    first_audio = True
    gen_resolution = set()

    return_video_source = ''

    for x in info['formats']:
        idx = x['format_id']
        if (idx in audio_list) and first_audio:
            first_audio = False
            return_video_source += "<audio preload id=\"audio\">"
            return_video_source = return_video_source + "<source src=" + quote + x[
                'url'] + quote + ' ' + "type=" + quote + audio_type[idx] + quote + ' ' + "/>" + '\n'
            return_video_source += "</audio>\n"

        if (idx in resolution) and (resolution[idx] not in gen_resolution):
            gen_resolution.add(resolution[idx])
            if not first_video:
                return_video_source = return_video_source + "<source src=" + quote + x[
                    'url'] + quote + ' ' + "type=" + quote + video_type[idx] + quote + ' ' + "label=" + quote + \
                                      resolution[idx] + "p" + quote + ' ' + "res=" + quote + resolution[
                                          idx] + quote + ' ' + "/>"
            else:
                first_video = False
                return_video_source = return_video_source + "<source src=" + quote + x[
                    'url'] + quote + ' ' + "type=" + quote + video_type[idx] + quote + ' ' + "label=" + quote + \
                                      resolution[idx] + "p" + quote + ' ' + "res=" + quote + resolution[
                                          idx] + quote + ' ' + "default label=" + quote + resolution[
                                          idx] + "p" + quote + ' ' + '/>\n'
    return return_video_source


@app.route('/play/<string:page_name>/')
def render_video(page_name):
    video_source = extract_url(page_name)
    return render_template('video_player_youtube.html', videosource=video_source)

@app.route('/graphs')
@http2push('static/graphs_push_manifest.json')
def render_graph():
    return render_template('graphs.html')

@app.route('/graphs-weights')
@http2push('static/graphs_weights_push_manifest.json')
def render_graph_weights():
    return render_template('graphs_weights.html')

@app.route('/graphs-js')
@http2push('static/graphs_js_push_manifest.json')
def render_graph_js():
	return render_template('graphs_js.html')

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True, port=5000)
    # app.run(debug=False, host='silver.cs.uchicago.edu', port=5000)
