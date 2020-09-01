animal = ['척추동물', '어류', '척추동물', '무척추동물', '파충류', '척추동물', '어류', '파충류']

def solution(animal, space ):
    chair = [] * space
    answer = 0

    for i in animal: 
        if len(chair) < 3:
            if i in chair:
                hit = chair.append(chair.index(i))
                chair.append(hit)
                answer += 1
            else:
                chair.append(i)
                answer += 60
        else:
            if i in chair:
                hit = chair.pop(chair.index(i))
                chair.append(hit)
                answer += 1
            else:
                chair.pop(0)
                chair.append(i)
                answer += 60

    return f'{answer//60}분 {answer%60} 초'

print(solution(animal, 3))