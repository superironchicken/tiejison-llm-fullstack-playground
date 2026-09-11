import { useState } from "react"

function App() {
	const [message, setMessage] = useState("")
	const [messages, setMessages] = useState([])
	const [stream, setStream] = useState(false)

	async function handleSubmit() {
		// [新增] 把本轮用户输入组装成一条消息
		const userMessage = { role: "user", content: message }
		// [新增] 手动拼出要发给后端的完整历史（不能用 messages 本身，
		// 因为 setMessages 是异步的，这里读到的还是旧值）
		const history = [...messages, userMessage]

		// [修改] 原来是 setResult("")，现在把用户消息追加进列表，界面上立刻能看到
		setMessages(history)
		// [新增] 清空输入框，方便连续提问
		setMessage("")

		const response = await fetch("http://127.0.0.1:8000/chat", {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				messages: history,
				stream: stream
			})
		})

		if (!stream) {
			const data = await response.json()
			setMessages((prev) => [
				...prev,
				{ role: "assistant", content: data.result }
			])
			return
		}

		setMessages((prev) => [
			...prev,
			{ role: "assistant", content: "" }
		])

		const reader = response.body.getReader()
		const decoder = new TextDecoder()

		while (true) {
			const { done, value } = await reader.read()
			if (done) break

			const chunk = decoder.decode(value, { stream: true })
			setMessages((prev) => {
				const updated = [...prev]
				const last = updated[updated.length - 1]
				updated[updated.length - 1] = {
					...last,
					content: last.content + chunk
				}
				return updated
			})
		}
	}

	return (
		<div>
			<div>
				<input
					type="text"
					value={message}
					onChange={(e) => setMessage(e.target.value)}
				/>
				<button onClick={handleSubmit}>发送</button>
				<label>
					<input
						type="checkbox"
						checked={stream}
						onChange={(e) => setStream(e.target.checked)}
					/>
					流式
				</label>
			</div>
			<div>
				{messages.map((msg, index) => (
					<div key={index}>
						<b>{msg.role === "user" ? "我" : "助手"}：</b>
						<span>{msg.content}</span>
					</div>
				))}
			</div>
		</div>
	)
}

export default App
