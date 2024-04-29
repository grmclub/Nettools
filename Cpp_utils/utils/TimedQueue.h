#ifndef MISC_TIMEDQUEUE_H
#define MISC_TIMEDQUEUE_H

#include <chrono>
#include <condition_variable>
#include <deque>
#include <mutex>
#include <string>
#include <utility>

#include "Exception.h"

namespace misc {

class EmptyQueueError : public Exception
{
public:
	explicit EmptyQueueError(const char* what) throw ()
		: Exception(what)
	{}

	explicit EmptyQueueError(const std::string& what) throw ()
		: Exception(what)
	{}
};

template <typename T, typename Container = std::deque<T>>
class LockedQueue
{
public:
	typedef typename Container::value_type      value_type;
	typedef typename Container::pointer         pointer;
	typedef typename Container::const_pointer   const_pointer;
	typedef typename Container::reference       reference;
	typedef typename Container::const_reference const_reference;
	typedef typename Container::size_type       size_type;
	typedef typename Container::allocator_type  allocator_type;
	typedef          Container                  container_type;

	LockedQueue() = default;

	~LockedQueue() = default;

	LockedQueue(const LockedQueue&) = delete;

	LockedQueue& operator =(const LockedQueue&) = delete;

	void push(const value_type&);

	void push(value_type&&);

	value_type pop();

	size_type size() const;

	bool empty() const;

private:
	typedef std::mutex mutex_type;
	typedef std::lock_guard<mutex_type> lock_guard_type;

	Container m_cont;
	mutable mutex_type m_mtx;

	void checkEmpty() const;
};

template <typename T, typename Container>
inline void LockedQueue<T, Container>::push(const value_type& val)
{
	lock_guard_type lk(m_mtx);
	m_cont.push_back(val);
}

template <typename T, typename Container>
inline void LockedQueue<T, Container>::push(value_type&& val)
{
	lock_guard_type lk(m_mtx);
	m_cont.push_back(std::move(val));
}

template <typename T, typename Container>
typename LockedQueue<T, Container>::value_type LockedQueue<T, Container>::pop()
{
	lock_guard_type lk(m_mtx);
	checkEmpty();
	value_type ret = std::move(m_cont.front());
	m_cont.pop_front();
	return std::move(ret);
}

template <typename T, typename Container>
inline typename LockedQueue<T, Container>::size_type LockedQueue<T, Container>::size() const
{
	lock_guard_type lk(m_mtx);
	return m_cont.size();
}

template <typename T, typename Container>
inline bool LockedQueue<T, Container>::empty() const
{
	lock_guard_type lk(m_mtx);
	return m_cont.empty();
}

template <typename T, typename Container>
inline void LockedQueue<T, Container>::checkEmpty() const
{
	if (m_cont.empty())
		throw EmptyQueueError("Empty queue");
}

template <typename T, typename Container = std::deque<T>>
class TimedQueue
{
public:
	typedef typename Container::value_type      value_type;
	typedef typename Container::pointer         pointer;
	typedef typename Container::const_pointer   const_pointer;
	typedef typename Container::reference       reference;
	typedef typename Container::const_reference const_reference;
	typedef typename Container::size_type       size_type;
	typedef typename Container::allocator_type  allocator_type;
	typedef          Container                  container_type;

	TimedQueue() = default;

	~TimedQueue() = default;

	TimedQueue(const TimedQueue&) = delete;

	TimedQueue& operator =(const TimedQueue&) = delete;

	void push(const value_type&);

	void push(value_type&&);

	value_type pop();

	value_type try_pop();

	template <typename Duration>
	value_type try_pop_until(const std::chrono::time_point<std::chrono::system_clock, Duration>&);

	template <typename Rep, typename Period>
	value_type try_pop_for(const std::chrono::duration<Rep, Period>&);

	void unblock() const;

	size_type size() const;

	bool empty() const;

private:
	typedef std::mutex mutex_type;
	typedef std::lock_guard<mutex_type> lock_guard_type;
	typedef std::unique_lock<mutex_type> unique_lock_type;

	Container m_cont;
	mutable mutex_type m_mtx;
	mutable std::condition_variable m_cv;

	void checkEmpty() const;
};

template <typename T, typename Container>
inline void TimedQueue<T, Container>::push(const value_type& val)
{
	lock_guard_type lk(m_mtx);
	m_cont.push_back(val);
	m_cv.notify_one();
}

template <typename T, typename Container>
inline void TimedQueue<T, Container>::push(value_type&& val)
{
	lock_guard_type lk(m_mtx);
	m_cont.push_back(std::move(val));
	m_cv.notify_one();
}

template <typename T, typename Container>
typename TimedQueue<T, Container>::value_type TimedQueue<T, Container>::pop()
{
	unique_lock_type lk(m_mtx);
	if (m_cont.empty()) {
		m_cv.wait(lk);
		checkEmpty();
	}
	value_type ret = std::move(m_cont.front());
	m_cont.pop_front();
	return std::move(ret);
}

template <typename T, typename Container>
typename TimedQueue<T, Container>::value_type TimedQueue<T, Container>::try_pop()
{
	lock_guard_type lk(m_mtx);
	checkEmpty();
	value_type ret = std::move(m_cont.front());
	m_cont.pop_front();
	return std::move(ret);
}

template <typename T, typename Container>
template <typename Duration>
typename TimedQueue<T, Container>::value_type TimedQueue<T, Container>::try_pop_until(
	const std::chrono::time_point<std::chrono::system_clock, Duration>& absTime)
{
	unique_lock_type lk(m_mtx);
	if (m_cont.empty()) {
		m_cv.wait_until(lk, absTime);
		checkEmpty();
	}
	value_type ret = std::move(m_cont.front());
	m_cont.pop_front();
	return std::move(ret);
}

template <typename T, typename Container>
template <typename Rep, typename Period>
inline typename TimedQueue<T, Container>::value_type TimedQueue<T, Container>::try_pop_for(
	const std::chrono::duration<Rep, Period>& relTime)
{
	return try_pop_until(std::chrono::system_clock::now() + relTime);
}

template <typename T, typename Container>
inline void TimedQueue<T, Container>::unblock() const
{
	m_cv.notify_one();
}

template <typename T, typename Container>
inline typename TimedQueue<T, Container>::size_type TimedQueue<T, Container>::size() const
{
	lock_guard_type lk(m_mtx);
	return m_cont.size();
}

template <typename T, typename Container>
inline bool TimedQueue<T, Container>::empty() const
{
	lock_guard_type lk(m_mtx);
	return m_cont.empty();
}

template <typename T, typename Container>
inline void TimedQueue<T, Container>::checkEmpty() const
{
	if (m_cont.empty())
		throw EmptyQueueError("Empty queue");
}

} // namespace misc

#endif // MISC_TIMEDQUEUE_H
