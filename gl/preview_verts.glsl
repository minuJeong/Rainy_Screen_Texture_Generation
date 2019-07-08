#version 460

in vec2 in_pos;
out vec2 vert_uv;

void main()
{
    vert_uv = in_pos * 0.5 + 0.5;
    vert_uv.x -= 0.5;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
