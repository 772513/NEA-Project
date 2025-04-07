scores = [1, 3, 4, 5, 6, 7, 8, 9, 10]
result = []

offset = 1
for turn in range(1, 11):
    if turn == scores[turn - offset]:
        result.append(scores[turn - offset])
    else:
        result.append("no score")
        offset += 1


# for turn in range(1, 11):
#     print(result)
#     for turn_number in range(0, turn):
#         print(turn, turn_number, scores[turn_number])
#         if turn == scores[turn_number]:
#             result.append(scores[turn_number])
#             break
#         if turn_number == turn - 1:
#             result.append("no score")

print(result)
