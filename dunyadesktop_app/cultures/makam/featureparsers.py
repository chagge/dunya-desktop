import copy
import os

import json
from essentia.standard import MonoLoader
import numpy as np

from cultures.makam import utilities
from cultures.makam import svgparser


DOCS_PATH = os.path.join(os.path.dirname(__file__), '..', 'documents')


def read_raw_audio(audio_path):
    raw_audio = np.array(MonoLoader(filename=audio_path)())
    len_audio = np.size(raw_audio)
    min_audio = np.min(raw_audio)
    max_audio = np.min(raw_audio)
    return raw_audio, len_audio, min_audio, max_audio


def load_pitch(pitch_path):
    pitch_data = json.load(open(pitch_path))
    pp = np.array(pitch_data['pitch'])

    time_stamps = pp[:, 0]
    pitch_curve = pp[:, 1]
    pitch_plot = copy.copy(pitch_curve)
    pitch_plot[pitch_plot < 20] = np.nan

    samplerate = pitch_data['sampleRate']
    hopsize = pitch_data['hopSize']

    max_pitch = np.max(pitch_curve)
    min_pitch = np.min(pitch_curve)

    return time_stamps, pitch_plot, max_pitch, min_pitch, samplerate, hopsize


def load_pd(pd_path):
    pd = json.load(open(pd_path))
    vals = pd["vals"]
    bins = pd["bins"]
    return vals, bins


def load_tonic(tonic_path):
    tnc = json.load(open(tonic_path))
    try:
        return [tnc['value']]
    except KeyError:
        return [work['value'] for work in tnc.values()]


def get_feature_paths(recid):
    doc_folder = os.path.join(DOCS_PATH, recid)
    (full_names, folders, names) = \
        utilities.get_filenames_in_dir(dir_name=doc_folder, keyword='*.json')

    paths = {'audio_path': os.path.join(doc_folder, recid + '.mp3')}
    for xx, name in enumerate(names):
        paths[name.split('.json')[0]] = full_names[xx]
    return paths


def load_notes(notes_path):
    notes = json.load(open(notes_path))
    return notes


def get_sections(sections_path):
    sections_dict = json.load(open(sections_path))
    metadata_path = sections_path.split('jointanalysis--sections.json')[0] + \
                    'audioanalysis--metadata.json'

    metadata = json.load(open(metadata_path))

    for work in metadata['works']:
        workid = work['mbid']
        title = work['title']

        try:
            for section in sections_dict[workid]:
                section['title'] = title
        except KeyError:
            pass

    return sections_dict


def generate_score_map(mbid):
    SCORE_PATH = os.path.join(os.path.dirname(__file__), '..', 'scores', mbid)
    fullnames, folders, names = utilities.get_filenames_in_dir(SCORE_PATH,
                                                               '*.svg')
    notes = {}
    for p in fullnames:
        tree, root = svgparser.initialize_svg(p)
        notes_dict = svgparser.get_note_indexes(p, root)
        notes.update(notes_dict)
    return notes
