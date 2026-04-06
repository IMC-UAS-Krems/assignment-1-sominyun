"""
platform.py
-----------
Implement the central StreamingPlatform class that orchestrates all domain entities
and provides query methods for analytics.

Classes to implement:
  - StreamingPlatform
"""
from datetime import datetime, timedelta

from .albums import Album
from .artists import Artist
from .playlists import Playlist, CollaborativePlaylist
from .sessions import ListeningSession
from .tracks import Track, Song
from .users import User, FreeUser, PremiumUser, FamilyMember, FamilyAccountUser


class StreamingPlatform:
    def __init__(self, name: str):
        self.name = name
        self.catalogue: dict[str, Track] = {}
        self.users: dict[str, User] = {}
        self.artists: dict[str, Artist] = {}
        self.albums: dict[str, Album] = {}
        self.playlists: list[Playlist] = []
        self.sessions: list[ListeningSession] = []

    def add_track(self, track: Track):
        self.catalogue[track.track_id] = track

    def add_user(self, user: User):
        self.users[user.user_id] = user

    def add_artist(self, artist: Artist):
        self.artists[artist.artist_id] = artist

    def add_album(self, album: Album):
        self.albums[album.album_id] = album

    def add_playlist(self, playlist: Playlist):
        self.playlists.append(playlist)

    def record_session(self, session: ListeningSession):
        self.sessions.append(session)
        session.user.add_session(session)

    def get_track(self, track_id: str) -> Track | None:
        return self.catalogue.get(track_id)

    def get_user(self, user_id: str) -> User | None:
        return self.users.get(user_id)

    def get_artist(self, artist_id: str) -> Artist | None:
        return self.artists.get(artist_id)

    def get_album(self, album_id: str) -> Album | None:
        return self.albums.get(album_id)

    def all_users(self) -> list[User]:
        return list(self.users.values())

    def all_tracks(self) -> list[Track]:
        return list(self.catalogue.values())

    # Q1
    def total_listening_time_minutes(self, start: datetime, end: datetime) -> float:
        total = 0
        for s in self.sessions:
            if start <= s.timestamp <= end:
                total += s.duration_listened_seconds
        return total / 60.0

    # Q2
    def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
        cutoff = datetime.now() - timedelta(days=days)
        premium_users = [
            u for u in self.all_users() if isinstance(u, PremiumUser)
        ]
        if not premium_users:
            return 0.0

        totals = []
        for user in premium_users:
            unique = {
                s.track.track_id
                for s in user.sessions
                if s.timestamp >= cutoff
            }
            totals.append(len(unique))
        return sum(totals) / len(totals) if totals else 0.0

    # Q3
    def track_with_most_distinct_listeners(self) -> Track | None:
        if not self.sessions:
            return None
        listener_count: dict[str, set[str]] = {}
        for s in self.sessions:
            tid = s.track.track_id
            if tid not in listener_count:
                listener_count[tid] = set()
            listener_count[tid].add(s.user.user_id)

        if not listener_count:
            return None
        max_tid = max(listener_count, key=lambda tid: len(listener_count[tid]))
        return self.get_track(max_tid)

    # Q4
    def avg_session_duration_by_user_type(self) -> list[tuple[str, float]]:
        from collections import defaultdict

        durations: dict[str, list[int]] = defaultdict(list)

        for s in self.sessions:
            user = s.user
            if isinstance(user, FamilyMember):
                typ = "FamilyMember"
            elif isinstance(user, FamilyAccountUser):
                typ = "FamilyAccountUser"
            elif isinstance(user, PremiumUser):
                typ = "PremiumUser"
            elif isinstance(user, FreeUser):
                typ = "FreeUser"
            else:
                typ = "User"
            durations[typ].append(s.duration_listened_seconds)

        result = []
        for typ, secs in durations.items():
            avg = sum(secs) / len(secs) if secs else 0.0
            result.append((typ, avg))

        result.sort(key=lambda x: x[1], reverse=True)
        return result

    # Q5
    def total_listening_time_underage_sub_users_minutes(self, age_threshold: int = 18) -> float:
        total = 0
        for s in self.sessions:
            if isinstance(s.user, FamilyMember) and s.user.age < age_threshold:
                total += s.duration_listened_seconds
        return total / 60.0

    # Q6
    def top_artists_by_listening_time(self, n: int = 5) -> list[tuple[Artist, float]]:
        artist_time: dict[str, float] = {}
        for s in self.sessions:
            track = s.track
            if isinstance(track, Song) and track.artist:
                aid = track.artist.artist_id
                if aid not in artist_time:
                    artist_time[aid] = 0.0
                artist_time[aid] += s.duration_listened_seconds / 60.0

        sorted_artists = sorted(
            artist_time.items(), key=lambda x: x[1], reverse=True
        )[:n]

        result = []
        for aid, minutes in sorted_artists:
            artist = self.get_artist(aid)
            if artist:
                result.append((artist, minutes))
        return result

    # Q7
    def user_top_genre(self, user_id: str) -> tuple[str, float] | None:
        user = self.get_user(user_id)
        if not user or not user.sessions:
            return None

        genre_time: dict[str, int] = {}
        total = 0
        for s in user.sessions:
            g = s.track.genre
            genre_time[g] = genre_time.get(g, 0) + s.duration_listened_seconds
            total += s.duration_listened_seconds

        if not total:
            return None

        top_genre = max(genre_time, key=genre_time.get)
        percentage = (genre_time[top_genre] / total) * 100
        return top_genre, percentage

    # Q8
    def collaborative_playlists_with_many_artists(
            self, threshold: int = 3
    ) -> list[CollaborativePlaylist]:
        result = []
        for pl in self.playlists:
            if not isinstance(pl, CollaborativePlaylist):
                continue
            artists: set[str] = set()
            for t in pl.tracks:
                if isinstance(t, Song) and t.artist:
                    artists.add(t.artist.artist_id)
            if len(artists) > threshold:
                result.append(pl)
        return result

    # Q9
    def avg_tracks_per_playlist_type(self) -> dict[str, float]:
        counts: dict[str, list[int]] = {
            "Playlist": [],
            "CollaborativePlaylist": [],
        }

        for pl in self.playlists:
            if isinstance(pl, CollaborativePlaylist):
                key = "CollaborativePlaylist"
            else:
                key = "Playlist"
            counts[key].append(len(pl.tracks))

        result = {}
        for k, lst in counts.items():
            result[k] = sum(lst) / len(lst) if lst else 0.0
        return result

    # Q10
    def users_who_completed_albums(self) -> list[tuple[User, list[str]]]:
        result = []
        for user in self.all_users():
            completed = []
            listened_tracks: set[str] = user.unique_tracks_listened()

            for album in self.albums.values():
                if not album.tracks:
                    continue
                album_ids = {t.track_id for t in album.tracks}
                if album_ids.issubset(listened_tracks):
                    completed.append(album.title)

            if completed:
                result.append((user, completed))
        return result
