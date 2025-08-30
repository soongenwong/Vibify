"""
Weaviate Integration for Music Analysis Storage

This module handles storing and retrieving music analysis results as vectors
in Weaviate database for similarity search and recommendations.
"""

import weaviate
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone
import uuid as uuid_module
from weaviate.util import generate_uuid5
import weaviate.classes as wvc


class WeaviateMusicDB:
    """Weaviate database manager for music analysis storage"""
    
    def __init__(self, weaviate_url: str = "http://localhost:8080", api_key: Optional[str] = None):
        """
        Initialize Weaviate client
        
        Args:
            weaviate_url: Weaviate instance URL
            api_key: Optional API key for Weaviate Cloud
        """
        try:
            print(f"🔗 Attempting to connect to: {weaviate_url}")
            
            if api_key and ("weaviate.network" in weaviate_url or "weaviate.cloud" in weaviate_url or "weaviate.io" in weaviate_url or "gcp.weaviate.cloud" in weaviate_url):
                # For Weaviate Cloud - ensure URL is clean
                clean_url = weaviate_url.strip()
                if not clean_url.startswith("https://"):
                    clean_url = f"https://{clean_url}"
                
                print(f"   Using Weaviate Cloud at: {clean_url}")
                self.client = weaviate.connect_to_weaviate_cloud(
                    cluster_url=clean_url,
                    auth_credentials=wvc.init.Auth.api_key(api_key)
                )
            else:
                # For local Weaviate instance
                if weaviate_url.startswith("http"):
                    # Extract host and port from full URL
                    clean_host = weaviate_url.replace("http://", "").replace("https://", "")
                    if ":" in clean_host:
                        host, port = clean_host.split(":", 1)
                        port = int(port)
                    else:
                        host = clean_host
                        port = 8080
                else:
                    host = weaviate_url
                    port = 8080
                
                print(f"   Using local Weaviate at: {host}:{port}")
                self.client = weaviate.connect_to_local(host=host, port=port)
            
            # Test connection
            if self.client.is_ready():
                print(f"✅ Connected to Weaviate successfully!")
            else:
                raise ConnectionError("Weaviate is not ready")
                
        except Exception as e:
            print(f"❌ Failed to connect to Weaviate: Connection to Weaviate failed. Details: Error: {e}")
            print(f"Is Weaviate running and reachable at {weaviate_url}?")
            print(f"   URL provided: {weaviate_url}")
            print(f"   Please check:")
            print(f"   - URL format should be: https://your-cluster-name.weaviate.network")
            print(f"   - API key should be valid")
            print(f"   - Cluster should be running")
            self.client = None
    
    def create_music_collection(self) -> bool:
        """
        Create the MusicAnalysis collection schema in Weaviate
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            return False
            
        collection_name = "MusicAnalysis"
        
        # Check if collection already exists
        try:
            if self.client.collections.exists(collection_name):
                print(f"✅ Collection '{collection_name}' already exists")
                return True
        except:
            pass
        
        try:
            # Create collection with v4 client syntax - use default vectorizer
            self.client.collections.create(
                name=collection_name,
                description="Music analysis results with musical features and characteristics",
                # Use default vectorizer or none - let Weaviate Cloud decide
                properties=[
                    wvc.config.Property(
                        name="songName",
                        data_type=wvc.config.DataType.TEXT,
                        description="Name of the analyzed song"
                    ),
                    wvc.config.Property(
                        name="filePath",
                        data_type=wvc.config.DataType.TEXT,
                        description="Original file path of the audio"
                    ),
                    wvc.config.Property(
                        name="analysisText",
                        data_type=wvc.config.DataType.TEXT,
                        description="Text description of musical features for vectorization"
                    ),
                    wvc.config.Property(
                        name="rawFeatures",
                        data_type=wvc.config.DataType.TEXT,
                        description="JSON string of raw analysis features"
                    ),
                    wvc.config.Property(
                        name="timestamp",
                        data_type=wvc.config.DataType.DATE,
                        description="When the analysis was performed"
                    ),
                    wvc.config.Property(
                        name="tempo",
                        data_type=wvc.config.DataType.NUMBER,
                        description="Estimated tempo in BPM"
                    ),
                    wvc.config.Property(
                        name="pitchRangeMin",
                        data_type=wvc.config.DataType.NUMBER,
                        description="Minimum pitch (MIDI note number)"
                    ),
                    wvc.config.Property(
                        name="pitchRangeMax",
                        data_type=wvc.config.DataType.NUMBER,
                        description="Maximum pitch (MIDI note number)"
                    ),
                    wvc.config.Property(
                        name="noteCount",
                        data_type=wvc.config.DataType.INT,
                        description="Total number of notes detected"
                    ),
                    wvc.config.Property(
                        name="songDuration",
                        data_type=wvc.config.DataType.NUMBER,
                        description="Duration of the song in seconds"
                    ),
                    wvc.config.Property(
                        name="noteDensity",
                        data_type=wvc.config.DataType.NUMBER,
                        description="Notes per second"
                    )
                ]
            )
            
            print(f"✅ Created collection '{collection_name}'")
            return True
        except Exception as e:
            print(f"❌ Failed to create collection: {e}")
            return False
    
    def convert_features_to_text(self, features: Dict[str, Any], song_name: str = "Unknown") -> str:
        """
        Convert musical features dictionary to descriptive text for vectorization
        
        Args:
            features: Musical features from MusicAnalyzer
            song_name: Name of the song
            
        Returns:
            str: Text description of musical characteristics
        """
        if features.get("error"):
            return f"Analysis failed for {song_name}: {features['error']}"
        
        # Extract key information
        pitch_info = features.get('pitch_range', {})
        rhythm_info = features.get('rhythm', {})
        dynamics_info = features.get('dynamics', {})
        temporal_info = features.get('temporal', {})
        harmony_info = features.get('harmony', {})
        
        # Build descriptive text
        text_parts = []
        
        # Song identification
        text_parts.append(f"Song: {song_name}")
        
        # Tempo and rhythm description
        tempo = temporal_info.get('tempo_estimate', 0)
        if tempo > 0:
            tempo_desc = self._describe_tempo(tempo)
            text_parts.append(f"Tempo: {tempo:.0f} BPM ({tempo_desc})")
        
        # Pitch characteristics
        pitch_min = pitch_info.get('min', 0)
        pitch_max = pitch_info.get('max', 0)
        pitch_mean = pitch_info.get('mean', 0)
        if pitch_max > pitch_min:
            text_parts.append(f"Pitch range from {self._midi_to_note(pitch_min)} to {self._midi_to_note(pitch_max)}")
            text_parts.append(f"Average pitch around {self._midi_to_note(pitch_mean)}")
        
        # Rhythm and density
        note_count = rhythm_info.get('total_notes', 0)
        note_density = rhythm_info.get('note_density', 0)
        avg_duration = rhythm_info.get('avg_duration', 0)
        
        text_parts.append(f"Contains {note_count} notes with density of {note_density:.1f} notes per second")
        text_parts.append(f"Average note duration of {avg_duration:.2f} seconds")
        
        # Dynamics description
        avg_velocity = dynamics_info.get('avg_velocity', 0)
        velocity_range = dynamics_info.get('velocity_range', 0)
        dynamics_desc = self._describe_dynamics(avg_velocity, velocity_range)
        text_parts.append(f"Dynamics: {dynamics_desc}")
        
        # Key and harmony hints
        pitch_classes = harmony_info.get('pitch_classes', {})
        if pitch_classes:
            common_notes = sorted(pitch_classes.items(), key=lambda x: x[1], reverse=True)[:3]
            common_note_names = [note[0] for note in common_notes]
            text_parts.append(f"Most prominent notes: {', '.join(common_note_names)}")
        
        # Musical style inference
        style_desc = self._infer_musical_style(features)
        if style_desc:
            text_parts.append(f"Musical characteristics: {style_desc}")
        
        return ". ".join(text_parts) + "."
    
    def _describe_tempo(self, bpm: float) -> str:
        """Convert BPM to descriptive tempo marking"""
        if bpm < 60:
            return "very slow"
        elif bpm < 76:
            return "slow"
        elif bpm < 108:
            return "moderate"
        elif bpm < 120:
            return "moderately fast"
        elif bpm < 168:
            return "fast"
        else:
            return "very fast"
    
    def _midi_to_note(self, midi_num: float) -> str:
        """Convert MIDI note number to note name"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = int(midi_num // 12) - 1
        note = notes[int(midi_num % 12)]
        return f"{note}{octave}"
    
    def _describe_dynamics(self, avg_velocity: float, velocity_range: float) -> str:
        """Describe dynamics based on velocity"""
        if avg_velocity < 40:
            intensity = "soft"
        elif avg_velocity < 80:
            intensity = "moderate"
        else:
            intensity = "loud"
        
        if velocity_range < 20:
            variation = "consistent"
        elif velocity_range < 50:
            variation = "varied"
        else:
            variation = "highly dynamic"
        
        return f"{intensity} and {variation}"
    
    def _infer_musical_style(self, features: Dict[str, Any]) -> str:
        """Infer musical style characteristics from features"""
        tempo = features.get('temporal', {}).get('tempo_estimate', 0)
        note_density = features.get('rhythm', {}).get('note_density', 0)
        pitch_std = features.get('pitch_range', {}).get('std', 0)
        
        characteristics = []
        
        # Tempo-based characteristics
        if tempo > 140:
            characteristics.append("energetic")
        elif tempo < 70:
            characteristics.append("relaxed")
        
        # Complexity based on note density
        if note_density > 5:
            characteristics.append("complex")
        elif note_density < 1:
            characteristics.append("sparse")
        
        # Melodic movement
        if pitch_std > 8:
            characteristics.append("melodically varied")
        elif pitch_std < 3:
            characteristics.append("melodically stable")
        
        return ", ".join(characteristics) if characteristics else "balanced"
    
    def store_analysis(self, features: Dict[str, Any], song_name: str, file_path: str) -> Optional[str]:
        """
        Store music analysis in Weaviate as a vector
        
        Args:
            features: Musical features from MusicAnalyzer
            song_name: Name of the song
            file_path: Original file path
            
        Returns:
            str: UUID of stored object, or None if failed
        """
        if not self.client:
            print("❌ No Weaviate connection available")
            return None
        
        # Ensure collection exists
        if not self.create_music_collection():
            return None
        
        # Convert features to descriptive text
        analysis_text = self.convert_features_to_text(features, song_name)
        
        # Create RFC3339 compliant timestamp with timezone
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Prepare object data
        properties = {
            "songName": song_name,
            "filePath": file_path,
            "analysisText": analysis_text,
            "rawFeatures": json.dumps(features),
            "timestamp": timestamp,  # Now RFC3339 compliant
        }
        
        # Add numerical features for filtering
        if not features.get("error"):
            properties.update({
                "tempo": float(features.get('temporal', {}).get('tempo_estimate', 0)),
                "pitchRangeMin": float(features.get('pitch_range', {}).get('min', 0)),
                "pitchRangeMax": float(features.get('pitch_range', {}).get('max', 0)),
                "noteCount": int(features.get('rhythm', {}).get('total_notes', 0)),
                "songDuration": float(features.get('temporal', {}).get('song_duration', 0)),
                "noteDensity": float(features.get('rhythm', {}).get('note_density', 0)),
            })
        
        try:
            # Generate deterministic UUID based on file path and song name
            deterministic_id = generate_uuid5({"songName": song_name, "filePath": file_path})
            
            # Get collection
            music_collection = self.client.collections.get("MusicAnalysis")
            
            # Insert object (Weaviate will automatically vectorize the analysisText)
            object_uuid = music_collection.data.insert(
                properties=properties,
                uuid=deterministic_id
            )
            
            print(f"✅ Stored analysis for '{song_name}' with UUID: {object_uuid}")
            return str(object_uuid)
            
        except Exception as e:
            print(f"❌ Failed to store analysis in Weaviate: {e}")
            return None
    
    def find_similar_songs(self, features: Dict[str, Any], song_name: str = "query", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar songs based on musical features
        
        Args:
            features: Musical features to search for
            song_name: Name for the query context
            limit: Number of similar songs to return
            
        Returns:
            List of similar song analysis results
        """
        if not self.client:
            print("❌ No Weaviate connection available")
            return []
        
        # Convert features to search text
        search_text = self.convert_features_to_text(features, song_name)
        
        try:
            music_collection = self.client.collections.get("MusicAnalysis")
            
            # Perform vector similarity search
            response = music_collection.query.near_text(
                query=search_text,
                limit=limit,
                return_metadata=wvc.query.MetadataQuery(distance=True)
            )
            
            results = []
            for obj in response.objects:
                result = {
                    "uuid": str(obj.uuid),
                    "song_name": obj.properties.get("songName"),
                    "file_path": obj.properties.get("filePath"),
                    "similarity_distance": obj.metadata.distance,
                    "tempo": obj.properties.get("tempo"),
                    "note_count": obj.properties.get("noteCount"),
                    "duration": obj.properties.get("songDuration"),
                    "analysis_text": obj.properties.get("analysisText"),
                    "timestamp": obj.properties.get("timestamp")
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Failed to search for similar songs: {e}")
            return []
    
    def find_songs_by_tempo(self, min_bpm: float, max_bpm: float, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find songs within a specific tempo range
        
        Args:
            min_bpm: Minimum BPM
            max_bpm: Maximum BPM
            limit: Number of results to return
            
        Returns:
            List of songs in the tempo range
        """
        if not self.client:
            return []
        
        try:
            music_collection = self.client.collections.get("MusicAnalysis")
            
            response = music_collection.query.fetch_objects(
                limit=limit,
                where=wvc.query.Filter.by_property("tempo").greater_or_equal(min_bpm)
            )
            
            # Filter by max tempo (combine with additional filter)
            results = []
            for obj in response.objects:
                tempo = obj.properties.get("tempo", 0)
                if tempo <= max_bpm:
                    results.append({
                        "song_name": obj.properties.get("songName"),
                        "tempo": tempo,
                        "file_path": obj.properties.get("filePath"),
                        "analysis_text": obj.properties.get("analysisText")
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Failed to search by tempo: {e}")
            return []
    
    def get_analysis_by_song_name(self, song_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve stored analysis by song name
        
        Args:
            song_name: Name of the song to find
            
        Returns:
            Analysis data or None if not found
        """
        if not self.client:
            return None
        
        try:
            music_collection = self.client.collections.get("MusicAnalysis")
            
            response = music_collection.query.fetch_objects(
                limit=1,
                where=wvc.query.Filter.by_property("songName").equal(song_name)
            )
            
            if response.objects:
                obj = response.objects[0]
                return {
                    "uuid": str(obj.uuid),
                    "song_name": obj.properties.get("songName"),
                    "file_path": obj.properties.get("filePath"),
                    "analysis_text": obj.properties.get("analysisText"),
                    "raw_features": json.loads(obj.properties.get("rawFeatures", "{}")),
                    "timestamp": obj.properties.get("timestamp")
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to retrieve analysis: {e}")
            return None
    
    def list_all_songs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List all stored song analyses
        
        Args:
            limit: Maximum number of songs to return
            
        Returns:
            List of all stored analyses
        """
        if not self.client:
            return []
        
        try:
            music_collection = self.client.collections.get("MusicAnalysis")
            
            response = music_collection.query.fetch_objects(limit=limit)
            
            results = []
            for obj in response.objects:
                results.append({
                    "song_name": obj.properties.get("songName"),
                    "tempo": obj.properties.get("tempo"),
                    "note_count": obj.properties.get("noteCount"),
                    "duration": obj.properties.get("songDuration"),
                    "timestamp": obj.properties.get("timestamp")
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Failed to list songs: {e}")
            return []
    
    def delete_analysis(self, song_name: str) -> bool:
        """
        Delete a stored analysis by song name
        
        Args:
            song_name: Name of the song to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            # First find the object
            analysis = self.get_analysis_by_song_name(song_name)
            if not analysis:
                print(f"❌ No analysis found for '{song_name}'")
                return False
            
            music_collection = self.client.collections.get("MusicAnalysis")
            
            # Delete by UUID
            music_collection.data.delete_by_id(analysis["uuid"])
            print(f"✅ Deleted analysis for '{song_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete analysis: {e}")
            return False
    
    def close(self):
        """Close Weaviate client connection"""
        if self.client:
            try:
                self.client.close()
                print("✅ Weaviate connection closed")
            except:
                pass


def extract_text_from_analysis(features: Dict[str, Any], song_name: str) -> str:
    """
    Standalone function to extract text from analysis features
    This can be used in main.py without creating a full Weaviate connection
    
    Args:
        features: Musical features from MusicAnalyzer
        song_name: Name of the song
        
    Returns:
        str: Text representation of the analysis
    """
    db = WeaviateMusicDB()  # Create instance just for text conversion
    return db.convert_features_to_text(features, song_name)


# Example usage functions
def store_music_analysis(features: Dict[str, Any], song_name: str, file_path: str, 
                        weaviate_url: str = "http://localhost:8080", 
                        api_key: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to store a music analysis in Weaviate
    
    Args:
        features: Musical features from MusicAnalyzer
        song_name: Name of the song
        file_path: Original file path
        weaviate_url: Weaviate instance URL
        api_key: Optional API key
        
    Returns:
        UUID of stored object or None if failed
    """
    db = WeaviateMusicDB(weaviate_url, api_key)
    if db.client:
        return db.store_analysis(features, song_name, file_path)
    return None


def search_similar_music(features: Dict[str, Any], song_name: str = "query",
                        limit: int = 5, weaviate_url: str = "http://localhost:8080",
                        api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to search for similar music
    
    Args:
        features: Musical features to search for
        song_name: Name for query context
        limit: Number of results
        weaviate_url: Weaviate instance URL
        api_key: Optional API key
        
    Returns:
        List of similar songs
    """
    db = WeaviateMusicDB(weaviate_url, api_key)
    if db.client:
        return db.find_similar_songs(features, song_name, limit)
    return []