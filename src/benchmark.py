import timeit

def benchmark(stmt: str, globals_dict: dict, number: int = 1000, repeat: int = 5):
    """
    Универсальный бенчмарк для замера времени выполнения.
    
    :param stmt: строка с кодом, который нужно замерить (например, 'r.movies.dist_by_year()')
    :param globals_dict: словарь с переменными, доступными в stmt (обычно globals())
    :param number: сколько раз выполнить код за один замер
    :param repeat: сколько раз повторить замер (берется лучшее время)
    :return: минимальное время выполнения
    """
    try:
        execution_time = min(timeit.repeat(
            stmt=stmt,
            globals=globals_dict,
            number=number,
            repeat=repeat
        ))
        
        print(f"Запрос: {stmt}")
        print(f"Всего запусков: {number}")
        print(f"Количество повторов: {repeat}")
        print(f"Лучшее время (на {number} запусков): {execution_time:.4f} сек.")
        print(f"Среднее время на 1 запуск: {execution_time / number * 1000:.4f} мс.")
        print("-" * 50)
        return execution_time
    except Exception as e:
        print(f"Ошибка при замере '{stmt}': {e}")
        return None