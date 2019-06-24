export const initialLayout = {
    'title': 'Inclination Chart',
    'margin': {
        'l': 10,
        'r': 10,
        'b': 10,
        't': 60,
    },
    'paper_bgcolor': '#FAFAFA',
    'hovermode': 'closest',
    'scene': {
        'aspectmode': 'manual',
        'aspectratio': {
            'x': 1,
            'y': 4,
            'z': 1
        },
        'camera': {
            'center': { 'x': -0.3316074267231184, 'y': -0.5704900622086274, 'z': -0.8053651445188535 },
            'eye': { 'x': 1.5417545350375266, 'y': -2.987277065249906, 'z': 2.349161002992645 },
            'up': { 'x': 0, 'y': 0, 'z': 1 }
        },
        'xaxis': {
            'title': 'Width (m)',
            'range': [0, 30],
            'showbackground': true,
            'backgroundcolor': 'rgb(230, 230,230)',
            'gridcolor': 'rgb(255, 255, 255)',
            'zerolinecolor': 'rgb(255, 255, 255)'
        },
        'yaxis': {
            'title': 'Length (m)',
            'range': [0, 120],
            'showbackground': true,
            'backgroundcolor': 'rgb(230, 230,230)',
            'gridcolor': 'rgb(255, 255, 255)',
            'zerolinecolor': 'rgb(255, 255, 255)'
        },
        'zaxis': {
            // 'rangemode': 'tozero',
            'title': 'Z (cm)',
            'range': [-1.5, 1.5],
            'showbackground': true,
            'backgroundcolor': 'rgb(230, 230,230)',
            'gridcolor': 'rgb(255, 255, 255)',
            'zerolinecolor': 'rgb(255, 255, 255)'
        }
    },
};

export const trace = {
    'type': 'mesh3d',
    'x': [],
    'y': [],
    'z': [],
    'intensity': [],
    'autocolorscale': true,
    'lighting': {
        'ambient': 1,
        'diffuse': 0.9,
        'fresnel': 0.5,
        'roughness': 0.9,
        'specular': 2
    },
    'flatshading': true,
    'reversescale': false
};