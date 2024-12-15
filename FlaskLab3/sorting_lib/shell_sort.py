# Функция сортировки методом Шелла
def shell_sort(arr, reverse=False):
    gap = len(arr) // 2
    while gap > 0:
        for value in range(gap, len(arr)):
            current_value = arr[value]
            pos = value

            if reverse:
                while pos >= gap and arr[pos - gap] < current_value:
                    arr[pos] = arr[pos - gap]
                    pos -= gap
            else:
                while pos >= gap and arr[pos - gap] > current_value:
                    arr[pos] = arr[pos - gap]
                    pos -= gap

            arr[pos] = current_value
        gap //= 2

    return arr
