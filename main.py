from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from pytube import YouTube
from pprint import pprint

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///youtube-downloader.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Youtube(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    video_url = db.Column(db.String(250), nullable=False)
    thumbnail_url = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"Youtube {self.title}"


# CREATE RECORD
db.create_all()


@app.route('/', methods=["GET", "POST"])
def home():
    global yt
    if request.method == "POST":
        url = request.form["url"]
        yt = YouTube(
            url,
            use_oauth=False,
            allow_oauth_cache=True
        )
        video = Youtube(
                        title=yt.title,
                        video_url=request.form["url"],
                        thumbnail_url=yt.thumbnail_url)

        db.session.add(video)
        db.session.commit()
        return redirect(url_for("video", title=yt.title))
        # print(yt.streams)
        # print(yt.streams.filter(file_extension='mp4'))

    return render_template("index.html")


@app.route("/video/<title>", methods=["GET", "POST"])
def video(title):
    # ytvideo = db.session.query(Youtube).filter_by(title=title).first()
    vid_title = yt.title
    image = yt.thumbnail_url
    # url = yt.video_url
    # yt = YouTube(url)
    pprint(yt.streams.filter(file_extension='mp4'))
    stream = yt.streams.filter(file_extension='mp4', progressive=True)
    return render_template("video.html", vid=yt, title=vid_title, img=image, streams=stream)


@app.route("/download/<resolution>")
def download(resolution):
    # print("hi")
    # print(resolution)
    stream = yt.streams.filter(file_extension='mp4').get_by_resolution(resolution)
    filename = stream.download()
    # return redirect(url_for("downloading", file=filename))
    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
