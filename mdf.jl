import JSON
using LinearAlgebra


function read_json()
    file = open("mdf_input.json")
    data = JSON.parse(file)
    close(file)
    return data
end



function output_json(_res)
    dict = Dict()
    push!(dict,"resultado"=>_res)
    open("mdf_output.json","w") do f
        JSON.print(f,dict)
    end
end


data = read_json()

matriz = Vector{Vector{Float64}}(data)
matriz_len = length(matriz)
line_tam = length(matriz[1])

matriz_system = Matrix{Int64}(undef,matriz_len,5)
matriz_system_result = Vector{Float64}(undef,matriz_len)

for i in 2:(matriz_len - 1)
    for j in 2:(line_tam - 1)
        if matriz[i][j] == -1.0
            matriz_system[i,1] = 4.0
            total = 0.0
            baixo = matriz[i - 1][j]
            cima = matriz[i + 1][j]
            esquerda = matriz[i][j - 1]
            direita = matriz[i][j + 1]
            if baixo == -1.0
                matriz_system[i,2] = -1.0
            else
                total += baixo
            end
            if cima == -1.0
                matriz_system[i,3] = -1.0
            else
                total += cima
            end
            if esquerda == -1.0
                matriz_system[i,4] = -1.0
            else
                total += esquerda
            end
            if direita == -1.0
                matriz_system[i,5] = -1.0
            else
                total += direita
            end
            matriz_system_result[i] = total
        end
    end
end

T_result = matriz_system\matriz_system_result

for i in 2:(matriz_len - 1)
    for j in 2:(line_tam - 1)
        if matriz[i][j] == -1.0
            total = 0.0
            baixo = matriz[i - 1][j]
            cima = matriz[i + 1][j]
            esquerda = matriz[i][j - 1]
            direita = matriz[i][j + 1]
            if baixo == -1.0
                total += T_result[2]
            else
                total += baixo
            end
            if cima == -1.0
                total += T_result[3]
            else
                total += cima
            end
            if esquerda == -1.0
                total += T_result[4]
            else
                total += esquerda
            end
            if direita == -1.0
                total += T_result[5]
            else
                total += direita
            end

            matriz[i][j] = round((total / 4), digits=2)
        end
    end
end

output_json(matriz)