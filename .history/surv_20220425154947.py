def survey(message = 'question'):
    answer = input('Please, input' + message + ':')
    return answer

users = []
while True:
    first_name = survey('first_name')