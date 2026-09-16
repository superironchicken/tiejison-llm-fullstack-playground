import { useState } from "react"

function App() {
	const [message, setMessage] = useState("")
	const [messages, setMessages] = useState([])
	const [stream, setStream] = useState(false)

	async function handleSubmit() {
		const userMessage = { role: "user", content: message }
		const history = [...messages, userMessage]
		setMessages(history)
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
